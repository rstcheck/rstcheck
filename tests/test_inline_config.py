"""Tests for ``inline_config`` module."""
from rstcheck import inline_config


class TestFindIgnoredLanguages:
    """Test ``find_ignored_languages`` function."""

    @staticmethod
    def test_empty_string_source() -> None:
        """Test giving an empty string as source results in no languages found."""
        source = ""

        result = list(inline_config.find_ignored_languages(source, "<string>"))

        assert not result

    @staticmethod
    def test_source_without_config() -> None:
        """Test giving source without config comment results in no languages found."""
        source = """
Example
=======
"""

        result = list(inline_config.find_ignored_languages(source, "<string>"))

        assert not result

    @staticmethod
    def test_source_with_correct_config() -> None:
        """Test giving source with correct config comment results in languages found."""
        source = """
Example
=======
.. rstcheck: ignore-languages=cpp
"""

        result = list(inline_config.find_ignored_languages(source, "<string>"))

        assert result == ["cpp"]

    @staticmethod
    def test_source_with_correct_config_multiple_languages() -> None:
        """Test giving source with correct config comment results in languages found.

        Test with multiple languages on one comment.
        """
        source = """
Example
=======
.. rstcheck: ignore-languages=cpp,json
"""

        result = list(inline_config.find_ignored_languages(source, "<string>"))

        assert result == ["cpp", "json"]

    @staticmethod
    def test_source_with_correct_config_multiple_comments() -> None:
        """Test giving source with correct config comment results in languages found.

        Test with multiple languages on different comments.
        """
        source = """
Example
=======
.. rstcheck: ignore-languages=cpp
.. rstcheck: ignore-languages=json
"""

        result = list(inline_config.find_ignored_languages(source, "<string>"))

        assert result == ["cpp", "json"]

    @staticmethod
    def test_source_with_correct_config_whitespace() -> None:
        """Test giving source with correct config comment results in languages found.

        Test whitspace around equal sign.
        """
        source = """
Example
=======
.. rstcheck: ignore-languages =cpp
.. rstcheck: ignore-languages= json
.. rstcheck: ignore-languages = python
"""

        result = list(inline_config.find_ignored_languages(source, "<string>"))

        assert result == ["cpp", "json", "python"]

    @staticmethod
    def test_source_with_incorrect_config_keyword_gets_ignored() -> None:
        """Test wrong config keyword results in no languages found."""
        source = """
Example
=======
.. rstcheck: ignore_languages=cpp
"""

        result = list(inline_config.find_ignored_languages(source, "<string>"))

        assert not result

    @staticmethod
    def test_source_with_incorrect_config_syntax_raises() -> None:
        """Test incorrect inline config is ignored."""
        source = """
Example
=======
.. rstcheck: ignore-languages: cpp
"""

        result = list(inline_config.find_ignored_languages(source, "<string>"))

        assert not result
