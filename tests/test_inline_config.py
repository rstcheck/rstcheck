"""Tests for ``inline_config`` module."""
import typing as t

import pytest

from rstcheck import _compat as _t, inline_config, types


def test_default_values_for_inline_config() -> None:
    """Test default values of  ``RstcheckConfigInline``."""
    result = inline_config.RstcheckConfigInline()

    assert result.ignore_directives is None
    assert result.ignore_roles is None
    assert result.ignore_substitutions is None
    assert result.ignore_languages is None


class TestSplitStrValidatorMethod:  # pylint: disable=duplicate-code
    """Test ``split_str`` validator method of the ``RstcheckConfigInline`` class.

    It validates the

    - ``ignore_directives``
    - ``ignore_roles``
    - ``ignore_substitutions``
    - ``ignore_languages``

    settings.
    """

    @staticmethod
    def test_none_means_default() -> None:
        """Test ``None`` results in unset ignore_messages."""
        result = inline_config.RstcheckConfigInline(
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
            ("value1, value2", ["value1", "value2"]),
            ("value1 ,value2", ["value1", "value2"]),
            ("value1 , value2", ["value1", "value2"]),
            ("value1 ,\n value2", ["value1", "value2"]),
            ("value1 ,\n value2\n", ["value1", "value2"]),
            ("value1 , value2,", ["value1", "value2"]),
            ("value1 , value2 ,", ["value1", "value2"]),
            ("value1 , value2 , ", ["value1", "value2"]),
        ],
    )
    def test_strings_are_transformed_to_lists(string: str, split_list: t.List[str]) -> None:
        """Test strings are split at the ",", trailing commas are ignored and whitespace cleaned."""
        result = inline_config.RstcheckConfigInline(
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
        ("string_list", "string_list_cleaned"),
        [
            (["value1"], ["value1"]),
            (["value1", "value2"], ["value1", "value2"]),
            (["value1", " value2"], ["value1", "value2"]),
            (["value1 ", "value2"], ["value1", "value2"]),
            (["value1 ", " value2"], ["value1", "value2"]),
        ],
    )
    def test_string_lists_are_whitespace_cleaned(
        string_list: t.List[str], string_list_cleaned: t.List[str]
    ) -> None:
        """Test lists of strings are whitespace cleaned."""
        result = inline_config.RstcheckConfigInline(
            ignore_languages=string_list,
            ignore_directives=string_list,
            ignore_roles=string_list,
            ignore_substitutions=string_list,
        )

        assert result is not None
        assert result.ignore_languages == string_list_cleaned
        assert result.ignore_directives == string_list_cleaned
        assert result.ignore_roles == string_list_cleaned
        assert result.ignore_substitutions == string_list_cleaned

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
            inline_config.RstcheckConfigInline(
                ignore_languages=value,
                ignore_directives=value,
                ignore_roles=value,
                ignore_substitutions=value,
            )


class TestInlineConfigGetter:
    """Test ``get_inline_config_from_source`` function."""

    @staticmethod
    def test_empty_string_source() -> None:
        """Test giving an empty string as source results in no config found."""
        source = ""

        result = list(inline_config.get_inline_config_from_source(source, "<string>"))

        assert not result

    @staticmethod
    def test_source_without_config() -> None:
        """Test giving source without config comment results in no config found."""
        source = """
Example
=======
"""

        result = list(inline_config.get_inline_config_from_source(source, "<string>"))

        assert not result

    @staticmethod
    def test_source_with_correct_config() -> None:
        """Test giving source with correct config comment results in config found."""
        source = """
Example
=======
.. rstcheck: ignore-languages=cpp
"""

        result = list(inline_config.get_inline_config_from_source(source, "<string>"))

        assert result == [types.InlineConfig(key="ignore-languages", value="cpp")]

    @staticmethod
    def test_source_with_unknown_config() -> None:
        """Test unknown config in comments is ignored."""
        source = """
Example
=======
.. rstcheck: unknown-config=true
.. rstcheck: ignore_languages=json
"""

        result = list(inline_config.get_inline_config_from_source(source, "<string>"))

        assert not result

    @staticmethod
    def test_source_with_invalid_config_format_is_ignored() -> None:
        """Test unknown config in comments is ignored."""
        source = """
Example
=======
.. rstcheck: ignore-languages: cpp
"""

        result = list(inline_config.get_inline_config_from_source(source, "<string>"))

        assert not result

    @staticmethod
    def test_source_with_known_and_unknown_config() -> None:
        """Test unknown config comments are ignored when mixed with valid confg."""
        source = """
Example
=======
.. rstcheck: unknown-config=true
.. rstcheck: ignore-languages=cpp
"""

        result = list(inline_config.get_inline_config_from_source(source, "<string>"))

        assert result == [types.InlineConfig(key="ignore-languages", value="cpp")]

    @staticmethod
    def test_source_with_correct_config_multiple_values() -> None:
        """Test giving source with correct config comment results in values found.

        Test with multiple values on one comment.
        """
        source = """
Example
=======
.. rstcheck: ignore-languages=cpp,json
"""

        result = list(inline_config.get_inline_config_from_source(source, "<string>"))

        assert result == [types.InlineConfig(key="ignore-languages", value="cpp,json")]

    @staticmethod
    def test_source_with_correct_config_multiple_comments() -> None:
        """Test giving source with correct config comment results in configs found.

        Test with multiple configs on different comments.
        """
        source = """
Example
=======
.. rstcheck: ignore-languages=cpp
.. rstcheck: ignore-languages=json
"""

        result = list(inline_config.get_inline_config_from_source(source, "<string>"))

        assert result == [
            types.InlineConfig(key="ignore-languages", value="cpp"),
            types.InlineConfig(key="ignore-languages", value="json"),
        ]

    @staticmethod
    def test_source_with_correct_config_whitespace() -> None:
        """Test giving source with correct config comment results in configs found.

        Test whitspace around equal sign.
        """
        source = """
Example
=======
.. rstcheck: ignore-languages =cpp
.. rstcheck: ignore-languages= json
.. rstcheck: ignore-languages = python
"""

        result = list(inline_config.get_inline_config_from_source(source, "<string>"))

        assert result == [
            types.InlineConfig(key="ignore-languages", value="cpp"),
            types.InlineConfig(key="ignore-languages", value="json"),
            types.InlineConfig(key="ignore-languages", value="python"),
        ]

    @staticmethod
    def test_source_with_multiple_correct_configs() -> None:
        """Test source with multiple correct configs.

        Test whitspace around equal sign.
        """
        source = """
Example
=======
.. rstcheck: ignore-languages=cpp
.. rstcheck: ignore-roles=role
.. rstcheck: ignore-languages=python
.. rstcheck: ignore-directives=direct
"""

        result = list(inline_config.get_inline_config_from_source(source, "<string>"))

        assert result == [
            types.InlineConfig(key="ignore-languages", value="cpp"),
            types.InlineConfig(key="ignore-roles", value="role"),
            types.InlineConfig(key="ignore-languages", value="python"),
            types.InlineConfig(key="ignore-directives", value="direct"),
        ]


class TestConfigFilterAndSpliter:
    """Test ``_filter_config_and_split_values`` function."""

    @staticmethod
    def test_only_specified_config_is_used() -> None:
        """Test only specified config is returned."""
        source = """
Example
=======
.. rstcheck: unknown-config=true
.. rstcheck: ignore-languages=cpp
.. rstcheck: ignore-directives=directive1
"""

        result = list(
            inline_config._filter_config_and_split_values(  # pylint: disable=protected-access
                "ignore-languages", source, "<string>"
            )
        )

        assert result == ["cpp"]

    @staticmethod
    def test_configs_are_comma_splitted() -> None:
        """Test configs are split on comma."""
        source = """
Example
=======
.. rstcheck: ignore-languages=cpp,json
.. rstcheck: ignore-languages=python
"""

        result = list(
            inline_config._filter_config_and_split_values(  # pylint: disable=protected-access
                "ignore-languages", source, "<string>"
            )
        )

        assert result == ["cpp", "json", "python"]


class FindIgnoreFn(_t.Protocol):  # pylint: disable=too-few-public-methods # noqa: D101
    def __call__(  # noqa: D102
        self,
        source: str,
        source_origin: types.SourceFileOrString,
        warn_unknown_settings: bool = False,
    ) -> t.Generator[str, None, None]:
        ...


class TestFindIgnoredFunctions:
    """Test ``find_ignored_*`` function.

    - find_ignored_directives
    - find_ignored_roles
    - find_ignored_substitutions
    - find_ignored_languages
    """

    @staticmethod
    @pytest.mark.parametrize(
        ("target_config", "expected_result"),
        [
            (inline_config.find_ignored_directives, ["directive1"]),
            (inline_config.find_ignored_roles, ["role1"]),
            (inline_config.find_ignored_substitutions, ["substitution1"]),
            (inline_config.find_ignored_languages, ["cpp"]),
        ],
    )
    def test_only_target_config_is_used(
        target_function: FindIgnoreFn, expected_result: str
    ) -> None:
        """Test only targeted configs are returned."""
        source = """
Example
=======
.. rstcheck: unknown-config=true
.. rstcheck: ignore-directives=directive1
.. rstcheck: ignore-roles=role1
.. rstcheck: ignore-substitutions=substitution1
.. rstcheck: ignore-languages=cpp
"""

        result = list(target_function(source, "<string>"))

        assert result == expected_result

    @staticmethod
    @pytest.mark.parametrize(
        ("target_config", "expected_result"),
        [
            (inline_config.find_ignored_directives, ["directive1", "directive3", "directive2"]),
            (inline_config.find_ignored_roles, ["role1", "role3", "role2"]),
            (
                inline_config.find_ignored_substitutions,
                ["substitution1", "substitution3", "substitution2"],
            ),
            (inline_config.find_ignored_languages, ["cpp", "json", "python"]),
        ],
    )
    def test_values_are_comma_splitted(target_function: FindIgnoreFn, expected_result: str) -> None:
        """Test  config values are split on comma."""
        source = """
Example
=======
.. rstcheck: unknown-config=true
.. rstcheck: ignore-directives=directive1,directive3
.. rstcheck: ignore-directives=directive2
.. rstcheck: ignore-roles=role1,role3
.. rstcheck: ignore-roles=role2
.. rstcheck: ignore-substitutions=substitution1,substitution3
.. rstcheck: ignore-substitutions=substitution2
.. rstcheck: ignore-languages=cpp,json
.. rstcheck: ignore-languages=python
"""

        result = list(target_function(source, "<string>"))

        assert result == expected_result
