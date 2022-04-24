"""Rstcheck configuration functionality."""
import configparser
import contextlib
import enum
import pathlib
import typing

import pydantic

from . import _extras


if _extras.TOMLI_INSTALLED:  # pragma: no cover
    import tomli


CONFIG_FILES = [".rstcheck.cfg", "setup.cfg"]
if _extras.TOMLI_INSTALLED:
    CONFIG_FILES = [".rstcheck.cfg", "pyproject.toml", "setup.cfg"]


class ReportLevel(enum.Enum):
    """Report levels supported by docutils."""

    INFO = 1
    WARNING = 2
    ERROR = 3
    SEVERE = 4
    NONE = 5


ReportLevelMap = {
    "info": 1,
    "warning": 2,
    "error": 3,
    "severe": 4,
    "none": 5,
}
"""Map docutils report levels in text form to numbers."""


class RstcheckConfigFile(pydantic.BaseModel):  # pylint: disable=no-member
    """Rstcheck config file.

    :raises ValueError:: If setting has incorrect value or type
    :raises pydantic.error_wrappers.ValidationError:: If setting is not parsable into correct type
    """

    report_level: typing.Optional[ReportLevel]
    ignore_directives: typing.Optional[typing.List[str]]
    ignore_roles: typing.Optional[typing.List[str]]
    ignore_substitutions: typing.Optional[typing.List[str]]
    ignore_languages: typing.Optional[typing.List[str]]
    # NOTE: Pattern type-arg errors pydanic: https://github.com/samuelcolvin/pydantic/issues/2636
    ignore_messages: typing.Optional[typing.Pattern]  # type: ignore[type-arg]

    @pydantic.validator("report_level", pre=True)
    @classmethod
    def valid_report_level(cls, value: typing.Any) -> typing.Optional[ReportLevel]:  # noqa: ANN401
        """Validate the report_level setting.

        :param value: Value to validate
        :raises ValueError: If ``Value`` is not a valid docutils report level
        :return: Instance of ``ReportLevel`` or None if emptry string.
        """
        if value == "" or value is None:
            return None

        if isinstance(value, bool):
            raise ValueError("Invalid report level")

        if isinstance(value, str):
            if value.casefold() in set(ReportLevelMap):
                return ReportLevel(ReportLevelMap[value.casefold()])

            with contextlib.suppress(ValueError):
                value = int(value)

        if isinstance(value, int) and 1 <= value <= 5:
            return ReportLevel(value)

        raise ValueError("Invalid report level")

    @pydantic.validator(
        "ignore_directives", "ignore_roles", "ignore_substitutions", "ignore_languages", pre=True
    )
    @classmethod
    def split_str(cls, value: typing.Any) -> typing.Optional[typing.List[str]]:  # noqa: ANN401
        """Validate and parse the following ignore_* settings.

        - ignore_directives
        - ignore_roles
        - ignore_substitutions
        - ignore_languages

        Comma separated strings are split into a list.

        :param value: Value to validate
        :raises ValueError: If not a ``str`` or ``List[str]``
        :return: List of things to ignore in the respective category
        """
        if value is None:
            return None
        if isinstance(value, str):
            return value.split(",")
        if isinstance(value, list) and all(isinstance(v, str) for v in value):
            return value
        raise ValueError("Not a string or list of strings")

    @pydantic.validator("ignore_messages", pre=True)
    @classmethod
    def join_regex_str(cls, value: typing.Any) -> typing.Optional[str]:  # noqa: ANN401
        """Validate and concatenate the ignore_messages setting to a RegEx string.

        If a list ist given, the entries are concatenated with "|" to create an or RegEx.

        :param value: Value to validate
        :raises ValueError: If not a ``str`` or ``List[str]``
        :return: A RegEx string with messages to ignore
        """
        if value is None:
            return None
        if isinstance(value, list) and all(isinstance(v, str) for v in value):
            return r"|".join(value)
        if isinstance(value, str):
            return value
        raise ValueError("Not a string or list of strings")


class RstcheckConfig(RstcheckConfigFile):  # pylint: disable=too-few-public-methods
    """Rstcheck config.

    :raises ValueError:: If setting has incorrect value or type
    :raises pydantic.error_wrappers.ValidationError:: If setting is not parsable into correct type
    """

    check_paths: typing.List[pathlib.Path]
    config_path: typing.Optional[pathlib.Path]
    recursive: typing.Optional[bool]


class _RstcheckConfigINIFile(
    pydantic.BaseModel  # pylint: disable=no-member
):  # pylint: disable=too-few-public-methods
    """Type for [rstcheck] section in INI file.

    The types apply to the file's data before the parsing by ``RstcheckConfig`` is done.

    :raises pydantic.error_wrappers.ValidationError:: If setting is not parsable into correct type
    """

    report_level: pydantic.NoneStr = None  # pylint: disable=no-member
    ignore_directives: pydantic.NoneStr = None  # pylint: disable=no-member
    ignore_roles: pydantic.NoneStr = None  # pylint: disable=no-member
    ignore_substitutions: pydantic.NoneStr = None  # pylint: disable=no-member
    ignore_languages: pydantic.NoneStr = None  # pylint: disable=no-member
    ignore_messages: pydantic.NoneStr = None  # pylint: disable=no-member


def _load_config_from_ini_file(ini_file: pathlib.Path) -> typing.Optional[RstcheckConfigFile]:
    """Load, parse and validate rstcheck config from a ini file.

    :param ini_file: INI file to load config from
    :raises FileNotFoundError: If the file is not found
    :return: instance of ``RstcheckConfigFile`` or ``None`` on missing config section
    """
    if not ini_file.is_file():
        raise FileNotFoundError(f"{ini_file}")

    parser = configparser.ConfigParser()
    parser.read(ini_file)

    if not parser.has_section("rstcheck"):
        return None

    config_values_raw = dict(parser.items("rstcheck"))
    config_values_checked = _RstcheckConfigINIFile(**config_values_raw)
    config_values_parsed = RstcheckConfigFile(**config_values_checked.dict())

    return config_values_parsed


class _RstcheckConfigTOMLFile(
    pydantic.BaseModel  # pylint: disable=no-member,
):  # pylint: disable=too-few-public-methods
    """Type for [tool.rstcheck] section in TOML file.

    The types apply to the file's data before the parsing by ``RstcheckConfig`` is done.

    :raises pydantic.error_wrappers.ValidationError:: If setting is not parsable into correct type
    """

    report_level: typing.Optional[typing.Union[int, str]] = None
    ignore_directives: typing.Optional[typing.List[str]] = None
    ignore_roles: typing.Optional[typing.List[str]] = None
    ignore_substitutions: typing.Optional[typing.List[str]] = None
    ignore_languages: typing.Optional[typing.List[str]] = None
    ignore_messages: typing.Optional[typing.Union[str, typing.List[str]]] = None


def _load_config_from_toml_file(toml_file: pathlib.Path) -> typing.Optional[RstcheckConfigFile]:
    """Load, parse and validate rstcheck config from a TOML file.

    .. warning::

        Needs tomli installed!
        Use toml extra.

    :param toml_file: TOML file to load config from
    :raises ValueError: If the file is not a TOML file
    :raises FileNotFoundError: If the file is not found
    :return: instance of ``RstcheckConfigFile`` or ``None`` on missing config section
    """
    _extras.install_guard("tomli")

    if toml_file.suffix.casefold() != ".toml":
        raise ValueError("File is not a TOML file")

    if not toml_file.is_file():
        raise FileNotFoundError(f"{toml_file}")

    with open(toml_file, "rb") as toml_file_handle:
        toml_dict = tomli.load(toml_file_handle)

    optional_rstcheck_section = typing.Optional[typing.Dict[str, typing.Any]]
    rstcheck_section: optional_rstcheck_section = toml_dict.get("tool", {}).get("rstcheck")

    if rstcheck_section is None:
        return None

    config_values_checked = _RstcheckConfigTOMLFile(**rstcheck_section)
    config_values_parsed = RstcheckConfigFile(**config_values_checked.dict())

    return config_values_parsed
