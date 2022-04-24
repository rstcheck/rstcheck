"""Tests for ``config`` module."""
import pathlib
import re
import typing

import pytest

from rstcheck import _extras, config


def test_report_level_map_matches_numbers() -> None:  # noqa: AAA01
    """Test that the enum's values match the map's ones."""
    enum_values = [e.value for e in config.ReportLevel]
    map_values = list(config.ReportLevelMap.values())

    assert map_values == enum_values


def test_report_level_map_matches_names() -> None:  # noqa: AAA01
    """Test that the enum's name match the map's keys."""
    enum_names = [
        e.casefold()
        for e in config.ReportLevel._member_names_  # pylint: disable=protected-access,no-member
    ]
    map_keys = list(config.ReportLevelMap.keys())

    assert enum_names == map_keys


class TestReportLevelValidator:
    """Test ``valid_report_level`` validator method of the ``RstcheckConfig`` class.

    It validates the ``report`` setting.
    """

    @staticmethod
    def test_none_means_unset() -> None:
        """Test ``None`` results in unset report level."""
        result = config.RstcheckConfig(report=None)

        assert result is not None
        assert result.report is None

    @staticmethod
    def test_empty_string_means_unset() -> None:
        """Test empty string results in unset report level."""
        result = config.RstcheckConfig(report="")

        assert result is not None
        assert result.report is None

    @staticmethod
    @pytest.mark.parametrize(
        "level",
        [1, 2, 3, 4, 5, "info", "warning", "error", "severe", "none", "NONE", "None", "NoNe"],
    )
    def test_valid_report_levels(level: typing.Any) -> None:  # noqa: ANN401
        """Test valid report levels accepted by docutils."""
        result = config.RstcheckConfig(report=level)

        assert result is not None
        assert result.report is not None

    @staticmethod
    @pytest.mark.parametrize(
        "level",
        [-1, 0, 1.5, 6, 32, False, True, "information", "warn", "err", "critical", "fatal"],
    )
    def test_invalid_report_levels(level: typing.Any) -> None:  # noqa: ANN401
        """Test invalid report levels not accepted by docutils."""
        with pytest.raises(ValueError, match="Invalid report level"):
            config.RstcheckConfig(report=level)


class TestSplitStrValidator:
    """Test ``split_str`` validator method of the ``RstcheckConfig`` class.

    It validates the

    - ``ignore_directives``
    - ``ignore_roles``
    - ``ignore_substitutions``
    - ``ignore_languages``

    settings.
    """

    @staticmethod
    def test_none_means_unset() -> None:
        """Test ``None`` results in unset ignore_messages."""
        result = config.RstcheckConfig(
            ignore_languages=None,
            ignore_directives=None,
            ignore_roles=None,
            ignore_substitutions=None,
        )

        assert result is not None
        assert result.ignore_languages is None
        assert result.ignore_directives is None
        assert result.ignore_roles is None
        assert result.ignore_substitutions is None

    @staticmethod
    @pytest.mark.parametrize(
        ("string", "split_list"),
        [
            ("value1", ["value1"]),
            ("value1,value2", ["value1", "value2"]),
            ("value1, value2", ["value1", " value2"]),
            ("value1 ,value2", ["value1 ", "value2"]),
            ("value1 , value2", ["value1 ", " value2"]),
        ],
    )
    def test_strings_are_transformed_to_lists(string: str, split_list: typing.List[str]) -> None:
        """Test strings are split at the ","."""
        result = config.RstcheckConfig(
            ignore_languages=string,
            ignore_directives=string,
            ignore_roles=string,
            ignore_substitutions=string,
        )

        assert result is not None
        assert result.ignore_languages == split_list
        assert result.ignore_directives == split_list
        assert result.ignore_roles == split_list
        assert result.ignore_substitutions == split_list

    @staticmethod
    @pytest.mark.parametrize(
        "string_list",
        [
            ["value1"],
            ["value1", "value2"],
            ["value1", " value2"],
            ["value1 ", "value2"],
            ["value1 ", " value2"],
        ],
    )
    def test_string_lists_are_kept_the_same(string_list: typing.List[str]) -> None:
        """Test lists of strings are untouched."""
        result = config.RstcheckConfig(
            ignore_languages=string_list,
            ignore_directives=string_list,
            ignore_roles=string_list,
            ignore_substitutions=string_list,
        )

        assert result is not None
        assert result.ignore_languages == string_list
        assert result.ignore_directives == string_list
        assert result.ignore_roles == string_list
        assert result.ignore_substitutions == string_list

    @staticmethod
    @pytest.mark.parametrize(
        "value",
        [
            1,
            [1],
            1.1,
            [1.1],
            False,
            [False],
            True,
            [True],
            ["foo", 1],
        ],
    )
    def test_invalid_settings(value: str) -> None:
        """Test invalid settings."""
        with pytest.raises(ValueError, match="Not a string or list of strings"):
            config.RstcheckConfig(
                ignore_languages=value,
                ignore_directives=value,
                ignore_roles=value,
                ignore_substitutions=value,
            )


class TestJoinRegexStrValidator:
    """Test ``valid_report_level`` validator method of the ``RstcheckConfig`` class.

    It validates the ``ignore_messages`` setting.
    """

    @staticmethod
    def test_none_means_unset() -> None:
        """Test ``None`` results in unset ignore_messages."""
        result = config.RstcheckConfig(ignore_messages=None)

        assert result is not None
        assert result.ignore_messages is None

    @staticmethod
    def test_strings_are_parsed_as_regex() -> None:
        """Test strings are parsed as regex."""
        string = r"\d{4}\.[A-Z]+Test$"
        regex = re.compile(string)

        result = config.RstcheckConfig(ignore_messages=string)

        assert result is not None
        assert result.ignore_messages == regex

    @staticmethod
    def test_empty_strings_are_valid() -> None:
        """Test empty strings are parsed as regex too."""
        string = ""
        regex = re.compile(string)

        result = config.RstcheckConfig(ignore_messages=string)

        assert result is not None
        assert result.ignore_messages == regex

    @staticmethod
    def test_string_list_are_joined_and_parsed_as_regex() -> None:
        """Test ignore_messages string lists are joined with "|" and parsed as regex."""
        string_list = [r"\d{4}\.[A-Z]+Test$", r"\d{4}\.[A-Z]+Test2$", r"\d{4}\.[A-Z]+Test3$"]
        full_string = r"\d{4}\.[A-Z]+Test$|\d{4}\.[A-Z]+Test2$|\d{4}\.[A-Z]+Test3$"
        regex = re.compile(full_string)

        result = config.RstcheckConfig(ignore_messages=string_list)

        assert result is not None
        assert result.ignore_messages == regex

    @staticmethod
    @pytest.mark.parametrize(
        ("string_list", "full_string"), [([""], ""), (["", ""], "|"), ([], "")]
    )
    def test_list_with_empty_contents(string_list: typing.List[str], full_string: str) -> None:
        """Test list with empty contents are parsed as regex too."""
        regex = re.compile(full_string)

        result = config.RstcheckConfig(ignore_messages=string_list)

        assert result is not None
        assert result.ignore_messages == regex

    @staticmethod
    @pytest.mark.parametrize(
        "value",
        [
            1,
            [1],
            1.1,
            [1.1],
            False,
            [False],
            True,
            [True],
            ["foo", 1],
        ],
    )
    def test_invalid_settings(value: str) -> None:
        """Test invalid ignore_messages settings."""
        with pytest.raises(ValueError, match="Not a string or list of strings"):
            config.RstcheckConfig(ignore_messages=value)


class TestIniFileLoader:
    """Test ``load_config_from_ini_file``."""

    @staticmethod
    def test_missing_file_errors(tmp_path: pathlib.Path) -> None:
        """Test ``FileNotFoundError`` is raised on missing file."""
        conf_file = tmp_path / "config.ini"

        with pytest.raises(FileNotFoundError):
            config.load_config_from_ini_file(conf_file)

    @staticmethod
    def test_not_a_file_errors(tmp_path: pathlib.Path) -> None:
        """Test ``FileNotFoundError`` is raised when not file."""
        conf_file = tmp_path

        with pytest.raises(FileNotFoundError):
            config.load_config_from_ini_file(conf_file)

    @staticmethod
    def test_returns_none_on_missing_section(tmp_path: pathlib.Path) -> None:
        """Test ``None`` is returned on missing section."""
        conf_file = tmp_path / "config.ini"
        file_content = "[not-rstcheck]"
        conf_file.write_text(file_content)

        result = config.load_config_from_ini_file(conf_file)

        assert result is None

    @staticmethod
    def test_ignores_unsupported_settings(tmp_path: pathlib.Path) -> None:
        """Test unsupported settings are ignored."""
        conf_file = tmp_path / "config.ini"
        file_content = """[rstcheck]
        unsupported_feature=True
        """
        conf_file.write_text(file_content)

        result = config.load_config_from_ini_file(conf_file)

        assert result is not None

    @staticmethod
    def test_supported_settings_are_loaded(tmp_path: pathlib.Path) -> None:
        """Test supported settings are loaded."""
        conf_file = tmp_path / "config.ini"
        file_content = """[rstcheck]
        report=1
        ignore_directives=directive
        ignore_roles=role
        ignore_substitutions=substitution
        ignore_languages=language
        ignore_messages=message
        """
        conf_file.write_text(file_content)

        result = config.load_config_from_ini_file(conf_file)

        assert result is not None
        assert result.report == "1"
        assert result.ignore_directives == "directive"
        assert result.ignore_roles == "role"
        assert result.ignore_substitutions == "substitution"
        assert result.ignore_languages == "language"
        assert result.ignore_messages == "message"

    @staticmethod
    def test_file_with_mixed_supported_settings(tmp_path: pathlib.Path) -> None:
        """Test mix of supported and unsupported settings."""
        conf_file = tmp_path / "config.ini"
        file_content = """[rstcheck]
        report=1
        ignore_directives=directive
        unsupported_feature=True
        """
        conf_file.write_text(file_content)

        result = config.load_config_from_ini_file(conf_file)

        assert result is not None
        assert result.report == "1"
        assert result.ignore_directives == "directive"

    @staticmethod
    def test_file_with_mixed_supported_sections(tmp_path: pathlib.Path) -> None:
        """Test mix of rstcheck and other section."""
        conf_file = tmp_path / "config.ini"
        file_content = """[rstcheck]
        report=1
        ignore_directives=directive
        unsupported_feature=True

        [not-rstcheck]
        report=2
        ignore_directives=not-directive
        unsupported_feature=False
        """
        conf_file.write_text(file_content)

        result = config.load_config_from_ini_file(conf_file)

        assert result is not None
        assert result.report == "1"
        assert result.ignore_directives == "directive"


@pytest.mark.skipif(not _extras.TOMLI_INSTALLED, reason="Depends on toml extra.")
class TestTomlFileLoader:
    """Test ``load_config_from_toml_file``."""

    @staticmethod
    def test_wrong_file_suffix_errors(tmp_path: pathlib.Path) -> None:
        """Test ``ValueError`` is raised on wrong file suffix."""
        conf_file = tmp_path / "config.ini"
        conf_file.touch()

        with pytest.raises(ValueError, match="File is not a TOML file"):
            config.load_config_from_toml_file(conf_file)

    @staticmethod
    def test_missing_file_errors(tmp_path: pathlib.Path) -> None:
        """Test ``FileNotFoundError`` is raised on missing file."""
        conf_file = tmp_path / "config.toml"

        with pytest.raises(FileNotFoundError):
            config.load_config_from_toml_file(conf_file)

    @staticmethod
    def test_not_a_file_errors(tmp_path: pathlib.Path) -> None:
        """Test ``FileNotFoundError`` is raised when not file."""
        conf_file = tmp_path / "config.toml"
        conf_file.mkdir()

        with pytest.raises(FileNotFoundError):
            config.load_config_from_toml_file(conf_file)

    @staticmethod
    @pytest.mark.parametrize("invalid_section", ["[tool.not-rstcheck]", "[rstcheck]"])
    def test_returns_none_on_missing_section(tmp_path: pathlib.Path, invalid_section: str) -> None:
        """Test ``None`` is returned on missing section."""
        conf_file = tmp_path / "config.toml"
        conf_file.write_text(invalid_section)

        result = config.load_config_from_toml_file(conf_file)

        assert result is None

    @staticmethod
    def test_ignores_unsupported_settings(tmp_path: pathlib.Path) -> None:
        """Test unsupported settings are ignored."""
        conf_file = tmp_path / "config.toml"
        file_content = """[tool.rstcheck]
        unsupported_feature = true
        """
        conf_file.write_text(file_content)

        result = config.load_config_from_toml_file(conf_file)

        assert result is not None

    @staticmethod
    def test_supported_settings_are_loaded(tmp_path: pathlib.Path) -> None:
        """Test supported settings are loaded."""
        conf_file = tmp_path / "config.toml"
        file_content = """[tool.rstcheck]
        report = 1
        ignore_directives = ["directive"]
        ignore_roles = ["role"]
        ignore_substitutions = ["substitution"]
        ignore_languages = ["language"]
        ignore_messages = "message"
        """
        conf_file.write_text(file_content)

        result = config.load_config_from_toml_file(conf_file)

        assert result is not None
        assert result.report == 1
        assert result.ignore_directives == ["directive"]
        assert result.ignore_roles == ["role"]
        assert result.ignore_substitutions == ["substitution"]
        assert result.ignore_languages == ["language"]
        assert result.ignore_messages == "message"

    @staticmethod
    def test_file_with_mixed_supported_settings(tmp_path: pathlib.Path) -> None:
        """Test mix of supported and unsupported settings."""
        conf_file = tmp_path / "config.toml"
        file_content = """[tool.rstcheck]
        report = 1
        ignore_directives = ["directive"]
        unsupported_feature = true
        """
        conf_file.write_text(file_content)

        result = config.load_config_from_toml_file(conf_file)

        assert result is not None
        assert result.report == 1
        assert result.ignore_directives == ["directive"]

    @staticmethod
    def test_file_with_mixed_supported_sections(tmp_path: pathlib.Path) -> None:
        """Test mix of rstcheck and other section."""
        conf_file = tmp_path / "config.toml"
        file_content = """[tool.rstcheck]
        report = 1
        ignore_directives = ["directive"]
        unsupported_feature = true

        [tool.not-rstcheck]
        report = 2
        ignore_directives = "not-directive"
        unsupported_feature = false
        """
        conf_file.write_text(file_content)

        result = config.load_config_from_toml_file(conf_file)

        assert result is not None
        assert result.report == 1
        assert result.ignore_directives == ["directive"]

    @staticmethod
    @pytest.mark.parametrize(
        ("value", "parsed_value"),
        [
            ("none", "none"),
            ("1", 1),
            ("6", 6),
            ("true", "true"),
            ("non-supported-but-string", "non-supported-but-string"),
        ],
    )
    def test_report_level_as_strings(tmp_path: pathlib.Path, value: str, parsed_value: str) -> None:
        """Test report setting with string values.

        The function does no value validation therfore unsupported values should not error.
        """
        conf_file = tmp_path / "config.toml"
        file_content = f"""[tool.rstcheck]
        report = "{value}"
        """
        conf_file.write_text(file_content)

        result = config.load_config_from_toml_file(conf_file)

        assert result is not None
        assert result.report == parsed_value

    @staticmethod
    @pytest.mark.parametrize("value", [-1, 0, 1, 6, 32])
    def test_report_level_as_int(tmp_path: pathlib.Path, value: int) -> None:
        """Test report setting with integer values.

        The function does no value validation therfore unsupported values should not error.
        """
        conf_file = tmp_path / "config.toml"
        file_content = f"""[tool.rstcheck]
        report = {value}
        """
        conf_file.write_text(file_content)

        result = config.load_config_from_toml_file(conf_file)

        assert result is not None
        assert result.report == value

    @staticmethod
    def test_ignore_messages_as_str(tmp_path: pathlib.Path) -> None:
        """Test ignore_messages setting with string value."""
        conf_file = tmp_path / "config.toml"
        file_content = """[tool.rstcheck]
        ignore_messages = "some-regex"
        """
        conf_file.write_text(file_content)

        result = config.load_config_from_toml_file(conf_file)

        assert result is not None
        assert result.ignore_messages == "some-regex"

    @staticmethod
    def test_ignore_messages_as_list(tmp_path: pathlib.Path) -> None:
        """Test ignore_messages setting with list of strings value."""
        conf_file = tmp_path / "config.toml"
        file_content = """[tool.rstcheck]
        ignore_messages = ["some-regex"]
        """
        conf_file.write_text(file_content)

        result = config.load_config_from_toml_file(conf_file)

        assert result is not None
        assert result.ignore_messages == ["some-regex"]
