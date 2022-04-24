"""Rstcheck configuration functionality."""
import configparser
import contextlib
import enum
import pathlib
import re
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
    """Rstcheck config."""

    files: typing.Optional[typing.List[pathlib.Path]]
    config: typing.Optional[pathlib.Path]
    recursive: typing.Optional[bool]
    report: typing.Optional[ReportLevel]
    ignore_directives: typing.Optional[typing.List[str]]
    ignore_roles: typing.Optional[typing.List[str]]
    ignore_substitutions: typing.Optional[typing.List[str]]
    ignore_languages: typing.Optional[typing.List[str]]
    ignore_messages: typing.Optional[typing.Pattern[str]]

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
    def join_regex_str(
        cls, value: typing.Any  # noqa: ANN401
    ) -> typing.Optional[typing.Pattern[str]]:
        """Validate and parse the ignore_messages setting to a RegEx.

        If a list ist given, the entries are concatenated with "|" to create an or RegEx.

        :param value: Value to validate
        :raises ValueError: If not a ``str`` or ``List[str]``
        :return: A RegEx with messages to ignore
        """
        if value is None:
            return None
        if isinstance(value, list) and all(isinstance(v, str) for v in value):
            return re.compile(r"|".join(value))
        if isinstance(value, str):
            return re.compile(value)
        raise ValueError("Not a string or list of strings")


def load_config_from_ini_file(ini_file: pathlib.Path) -> typing.Optional[RstcheckConfig]:
    """Load rstcheck config from a ini file.

    :param ini_file: INI file to load config from
    :raises FileNotFoundError: If the file is not found
    :return: ``None`` if no config section is found in the file;
        instance of ``RstcheckConfig`` otherwise
    """
    if not ini_file.is_file():
        raise FileNotFoundError(f"{ini_file}")

    parser = configparser.ConfigParser()
    parser.read(ini_file)

    if not parser.has_section("rstcheck"):
        return None

    config_values = dict(parser.items("rstcheck"))

    return RstcheckConfig(**config_values)


RstcheckTOMLConfig = typing.Dict[str, typing.Union[str, typing.List[str]]]
"""Type for [tool.rstcheck] section in pyproject.toml file."""


def load_config_from_toml_file(toml_file: pathlib.Path) -> typing.Optional[RstcheckConfig]:
    """Load rstcheck config from a TOML file.

    .. note::

        Needs tomli installed. Use toml extra.

    :param toml_file: TOML file to load config from
    :raises ModuleNotFoundError: If ``tomli`` is not installed
    :raises ValueError: If the file is not a TOML file
    :raises FileNotFoundError: If the file is not found
    :return: ``None`` if no config section is found in the file;
        instance of ``RstcheckConfig`` otherwise
    """
    _extras.install_guard("tomli")

    if toml_file.suffix.casefold() != ".toml":
        ValueError("File is not a TOML file.")

    if not toml_file.is_file():
        raise FileNotFoundError(f"{toml_file}")

    with open(toml_file, "rb") as conf_file:
        config = tomli.load(conf_file)

    config_values: typing.Optional[RstcheckTOMLConfig] = config.get("tool", {}).get(
        "rstcheck", None
    )

    if config_values is None:
        return None

    return RstcheckConfig(**config_values)
