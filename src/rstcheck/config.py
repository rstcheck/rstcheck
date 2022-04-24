"""Rstcheck configuration functionality."""
import configparser
import contextlib
import enum
import pathlib
import typing

import pydantic

from . import _extras


if _extras.TOMLI_INSTALLED:
    import tomli


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


class RstcheckConfig(pydantic.BaseModel):  # pylint: disable=no-member
    """Rstcheck config.

    :raises ValueError:: If setting has incorrect value or type
    :raises pydantic.error_wrappers.ValidationError:: If setting is not parsable into correct type
    """

    files: typing.Optional[typing.List[pathlib.Path]]
    config: typing.Optional[pathlib.Path]
    recursive: typing.Optional[bool]
    report: typing.Optional[ReportLevel]
    ignore_directives: typing.Optional[typing.List[str]]
    ignore_roles: typing.Optional[typing.List[str]]
    ignore_substitutions: typing.Optional[typing.List[str]]
    ignore_languages: typing.Optional[typing.List[str]]
    # NOTE: Pattern type-arg errors pydanic: https://github.com/samuelcolvin/pydantic/issues/2636
    ignore_messages: typing.Optional[typing.Pattern]  # type: ignore[type-arg]

    @pydantic.validator("report", pre=True)
    @classmethod
    def valid_report_level(cls, value: typing.Any) -> typing.Optional[ReportLevel]:  # noqa: ANN401
        """Validate the report level setting.

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


class RstcheckConfigINIFile(pydantic.BaseModel):  # pylint: disable=no-member,too-few-public-methods
    """Type for [rstcheck] section in INI file.

    The types apply to the file's data before the parsing by ``RstcheckConfig`` is done.

    :raises pydantic.error_wrappers.ValidationError:: If setting is not parsable into correct type
    """

    report: pydantic.NoneStr = None  # pylint: disable=no-member
    ignore_directives: pydantic.NoneStr = None  # pylint: disable=no-member
    ignore_roles: pydantic.NoneStr = None  # pylint: disable=no-member
    ignore_substitutions: pydantic.NoneStr = None  # pylint: disable=no-member
    ignore_languages: pydantic.NoneStr = None  # pylint: disable=no-member
    ignore_messages: pydantic.NoneStr = None  # pylint: disable=no-member


def load_config_from_ini_file(ini_file: pathlib.Path) -> typing.Optional[RstcheckConfigINIFile]:
    """Load rstcheck config from a ini file.

    .. caution::

        This function only does type and **no** value validation!

    :param ini_file: INI file to load config from
    :raises FileNotFoundError: If the file is not found
    :return: instance of ``RstcheckConfigINIFile`` or ``None`` on missing config section
    """
    if not ini_file.is_file():
        raise FileNotFoundError(f"{ini_file}")

    parser = configparser.ConfigParser()
    parser.read(ini_file)

    if not parser.has_section("rstcheck"):
        return None

    config_values = dict(parser.items("rstcheck"))

    return RstcheckConfigINIFile(**config_values)


class RstcheckConfigTOMLFile(
    pydantic.BaseModel  # pylint: disable=no-member,
):  # pylint: disable=too-few-public-methods
    """Type for [tool.rstcheck] section in TOML file.

    The types apply to the file's data before the parsing by ``RstcheckConfig`` is done.

    :raises pydantic.error_wrappers.ValidationError:: If setting is not parsable into correct type
    """

    report: typing.Optional[typing.Union[str, int]] = None
    ignore_directives: typing.Optional[typing.List[str]] = None
    ignore_roles: typing.Optional[typing.List[str]] = None
    ignore_substitutions: typing.Optional[typing.List[str]] = None
    ignore_languages: typing.Optional[typing.List[str]] = None
    ignore_messages: typing.Optional[typing.Union[str, typing.List[str]]] = None


def load_config_from_toml_file(toml_file: pathlib.Path) -> typing.Optional[RstcheckConfigTOMLFile]:
    """Load rstcheck config from a TOML file.

    .. caution::

        This function only does type and **no** value validation!

    .. warning::

        Needs tomli installed!
        Use toml extra.

    :param toml_file: TOML file to load config from
    :raises ValueError: If the file is not a TOML file
    :raises FileNotFoundError: If the file is not found
    :return: instance of ``RstcheckConfigTOMLFile`` or ``None`` on missing config section
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

    return RstcheckConfigTOMLFile(**rstcheck_section)
