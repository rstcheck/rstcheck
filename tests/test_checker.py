# pylint: disable=too-many-lines
"""Tests for ``checker`` module."""
import os
import pathlib
import re
import sys
from inspect import isfunction

import docutils.io
import docutils.nodes
import docutils.utils
import pytest

from rstcheck import _extras, checker, config, types


def test_check_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test ``check_file`` returns accumulated errors from ``check_source``."""
    errors = [
        types.LintError(source_origin="<string>", line_number=0, message=""),
        types.LintError(source_origin="<string>", line_number=1, message=""),
    ]
    monkeypatch.setattr(checker, "_get_source", lambda _: "source")
    monkeypatch.setattr(
        checker, "check_source", lambda _, source_file, ignores, report_level: (e for e in errors)
    )
    test_config = config.RstcheckConfig(config_path=pathlib.Path())

    result = checker.check_file(pathlib.Path(), test_config)

    assert result == errors


class TestRunConfigLoader:
    """Test ``_load_run_config`` function."""

    @staticmethod
    def test_global_config_path_set() -> None:
        """Test config path is set in main config.

        This results in no change -> return of main config.
        """
        test_config = config.RstcheckConfig(config_path=pathlib.Path())

        result = checker._load_run_config(  # pylint: disable=protected-access
            pathlib.Path(), test_config
        )

        assert result == test_config

    @staticmethod
    def test_no_config_file_in_dir_tree(monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config path is unset in main config and file dir tree has no config file.

        This results in no change -> return of main config.
        """
        monkeypatch.setattr(config, "load_config_file_from_dir_tree", lambda _: None)
        test_config = config.RstcheckConfig()

        result = checker._load_run_config(  # pylint: disable=protected-access
            pathlib.Path(), test_config
        )

        assert result == test_config

    @staticmethod
    def test_config_file_in_dir_tree(monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config path is unset in main config and file dir tree has a config file.

        This results in merge of configs -> return merged config.
        """
        test_file_config = config.RstcheckConfigFile(report_level=config.ReportLevel.SEVERE)
        monkeypatch.setattr(config, "load_config_file_from_dir_tree", lambda _: test_file_config)
        test_config = config.RstcheckConfig()

        result = checker._load_run_config(  # pylint: disable=protected-access
            pathlib.Path(), test_config, True
        )

        assert result is not None
        assert test_config != config.ReportLevel.SEVERE
        assert result.report_level == config.ReportLevel.SEVERE


class TestSourceGetter:
    """Test ``_get_source`` function."""

    @staticmethod
    def test_file_name_is_dash(monkeypatch: pytest.MonkeyPatch) -> None:
        """Test when file name is a dash, stdin is read."""
        source = "Teststring"
        monkeypatch.setattr(sys.stdin, "read", lambda: source)
        test_file = pathlib.Path("-")

        result = checker._get_source(test_file)  # pylint: disable=protected-access

        assert result == source

    @staticmethod
    def test_file_name_is_not_dash(tmp_path: pathlib.Path) -> None:
        """Test when file name is not a dash, the file is read."""
        source = """
Test
====
"""
        test_file = tmp_path / "testfile.rst"
        test_file.write_text(source)

        result = checker._get_source(test_file)  # pylint: disable=protected-access

        assert result == source


def test__replace_ignored_substitutions() -> None:
    """Test ``_replace_ignored_substitutions`` fucntion replaces substitutions."""
    source = "|Substitution1| |Substitution2|"

    result = checker._replace_ignored_substitutions(  # pylint: disable=protected-access
        source, ["Substitution1"]
    )

    assert result == "xSubstitution1x |Substitution2|"


def test__create_ignore_dict_from_config() -> None:
    """Test ``_create_ignore_dict_from_config`` fucntion creates ignore dict."""
    ignore_directives = ["code"]
    ignore_languages = ["python", "cpp"]
    ignore_messages = r"foo/bar"
    ignore_messages_re = re.compile(ignore_messages)
    ignore_substitutions = ["substi"]
    test_config = config.RstcheckConfig(
        ignore_directives=ignore_directives,
        ignore_languages=ignore_languages,
        ignore_messages=ignore_messages,
        ignore_substitutions=ignore_substitutions,
    )

    result = checker._create_ignore_dict_from_config(  # pylint: disable=protected-access
        test_config,
    )

    assert result == types.IgnoreDict(
        directives=ignore_directives,
        languages=ignore_languages,
        messages=ignore_messages_re,
        substitutions=ignore_substitutions,
    )


class TestSourceChecker:
    """Test ``check_source`` fucntion."""

    @staticmethod
    def test_empty_source() -> None:
        """Test empty source generates no errors."""
        source = ""

        result = list(checker.check_source(source))

        assert not result

    @staticmethod
    def test_lint_error_no_source_file() -> None:
        """Test lint error holds "<string>" if no source file is passed."""
        source = """
Test
===
"""

        result = list(checker.check_source(source))

        assert result[0]["source_origin"] == "<string>"

    @staticmethod
    def test_lint_error_with_source_file() -> None:
        """Test lint error holds source file."""
        test_file = pathlib.Path("test_file.rst")
        source = """
Test
===
"""

        result = list(checker.check_source(source, test_file))

        assert result[0]["source_origin"] == test_file

    @staticmethod
    def test_lint_error_returned_on_default_ignore() -> None:
        """Test lint error is returned with default ignores."""
        source = """
Test
===
"""

        result = list(checker.check_source(source))

        assert "Possible title underline, too short for the title" in result[0]["message"]

    @staticmethod
    def test_lint_error_skipped_on_set_ignore() -> None:
        """Test lint error is skipped with set ignores."""
        source = """
Test
===
"""
        ignores = types.IgnoreDict(
            messages=re.compile(r"Possible title underline, too short for the title"),
            languages=[],
            directives=[],
            substitutions=[],
        )

        result = list(checker.check_source(source, ignores=ignores))

        assert not result

    @staticmethod
    def test_invalid_inline_ignore_config() -> None:
        """Test error on invalid inline ignore-languages is passed on."""
        source = """
.. rstcheck: ignore-languages python
"""

        result = list(checker.check_source(source))

        assert 'Expected "key=value" syntax' in result[0].get("message", "")

    @staticmethod
    def test_invalid_inline_ignore_config_not_ignored() -> None:
        """Test error on invalid inline ignore-languages is not ignored."""
        source = """
.. rstcheck: ignore-languages python
"""
        ignores = types.IgnoreDict(
            messages=re.compile(r'Expected "key=value" syntax'),
            languages=[],
            directives=[],
            substitutions=[],
        )

        result = list(checker.check_source(source, ignores=ignores))

        assert 'Expected "key=value" syntax' in result[0]["message"]

    @staticmethod
    @pytest.mark.skipif(_extras.SPHINX_INSTALLED, reason="Test without sphinx extra.")
    def test_sphinx_directive_errors_without_sphinx() -> None:
        """Test error on sphinx directive when sphinx is missing."""
        source = """
.. py:function:: foo
"""

        result = list(checker.check_source(source))

        assert 'No directive entry for "py:function"' in result[0]["message"]

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    def test_sphinx_directive_does_not_error_with_sphinx() -> None:
        """Test no error on sphinx directive when sphinx is installed."""
        source = """
.. py:function:: foo
"""

        result = list(checker.check_source(source))

        assert not result

    @staticmethod
    @pytest.mark.skipif(sys.version_info > (3, 9), reason="Requires python3.9 or lower")
    def test_code_block_lint_error_returned_on_default_ignore_pre310() -> None:
        """Test code lint error is returned with default ignores.

        In Python version 3.10 the error messag changed.
        """
        source = """
.. code:: python

    print(
"""

        result = list(checker.check_source(source))

        assert "unexpected EOF while parsing" in result[0]["message"]

    @staticmethod
    @pytest.mark.skipif(sys.version_info > (3, 9), reason="Requires python3.9 or lower")
    def test_code_block_lint_error_on_set_ignore_not_ignored_pre310() -> None:
        """Test code lint error is not skipped with set ignores.

        In Python version 3.10 the error messag changed.
        """
        source = """
.. code:: python

    print(
"""
        ignores = types.IgnoreDict(
            messages=re.compile(r"unexpected EOF while parsing"),
            languages=[],
            directives=[],
            substitutions=[],
        )

        result = list(checker.check_source(source, ignores=ignores))

        assert "unexpected EOF while parsing" in result[0]["message"]

    @staticmethod
    @pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires python3.10 or higher")
    def test_code_block_lint_error_returned_on_default_ignore() -> None:
        """Test code lint error is returned with default ignores."""
        source = """
.. code:: python

    print(
"""

        result = list(checker.check_source(source))

        assert "'(' was never closed" in result[0]["message"]

    @staticmethod
    @pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires python3.10 or higher")
    def test_code_block_lint_error_on_set_ignore_not_ignored() -> None:
        """Test code lint error is not skipped with set ignores."""
        source = """
.. code:: python

    print(
"""
        ignores = types.IgnoreDict(
            messages=re.compile(r"unexpected EOF while parsing"),
            languages=[],
            directives=[],
            substitutions=[],
        )

        result = list(checker.check_source(source, ignores=ignores))

        assert "'(' was never closed" in result[0]["message"]


class TestCodeCheckRunner:
    """Test ``_run_code_checker_and_filter_errors`` function."""

    @staticmethod
    def test_without_ignore() -> None:
        """Test both checkers return error without ignore."""
        cb_checker = checker.CodeBlockChecker("<string>")
        checker_list = [
            cb_checker.create_checker("print(", "python"),
            cb_checker.create_checker("{", "json"),
        ]

        result = list(
            checker._run_code_checker_and_filter_errors(  # pylint: disable=protected-access
                checker_list, None
            )
        )

        assert len(result) == 2

    @staticmethod
    def test_with_ignore() -> None:
        """Test only one checker return error with ignore."""
        cb_checker = checker.CodeBlockChecker("<string>")
        checker_list = [
            cb_checker.create_checker("print(", "python"),
            cb_checker.create_checker("{", "json"),
        ]
        ignore_messages = re.compile(r"Expecting property name enclosed in double quotes")

        result = list(
            checker._run_code_checker_and_filter_errors(  # pylint: disable=protected-access
                checker_list, ignore_messages
            )
        )

        assert len(result) == 1


class TestRstErrorParseFilter:
    """Test ``_parse_and_filter_rst_errors`` function."""

    @staticmethod
    def test_without_ignore() -> None:
        """Test both error messages are parsed and returned."""
        error_str = "<string>:1:1: Error message 1\n<string>:1:2: Error message 2"

        result = list(
            checker._parse_and_filter_rst_errors(  # pylint: disable=protected-access
                error_str, "<string>", None
            )
        )

        assert len(result) == 2

    @staticmethod
    def test_with_ignore() -> None:
        """Test only one error message is parsed and returned."""
        error_str = "<string>:1:1: Error message 1\n<string>:1:2: Error message 2"
        ignore_messages = re.compile(r"Error message 1")

        result = list(
            checker._parse_and_filter_rst_errors(  # pylint: disable=protected-access
                error_str, "<string>", ignore_messages
            )
        )

        assert len(result) == 1


class TestCheckTranslator:  # pylint: disable=too-few-public-methods
    """Test ``_CheckTranslator`` class."""

    @staticmethod
    def test_no_checkers_on_init() -> None:
        """Test checkers are empty on init."""
        doc = docutils.utils.new_document("")

        result = checker._CheckTranslator(doc, "", "<string>")  # pylint: disable=protected-access

        assert not result.checkers


class TestCodeBlockChecker:  # pylint: disable=too-many-public-methods
    """Test ``CodeBlockChecker`` class."""

    @staticmethod
    def test_init() -> None:
        """Test nothing special happens on ``__init__`` method."""
        source_origin: types.SourceFileOrString = "<string>"

        result = checker.CodeBlockChecker(source_origin)

        assert result.source_origin == source_origin
        assert result.ignores is None
        assert result.report_level == config.ReportLevel.INFO

    @staticmethod
    def test_language_is_supported_on_supported_lang() -> None:
        """Test ``language_is_supported`` method returns ``True`` for supported language."""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = cb_checker.language_is_supported("python")

        assert result is True

    @staticmethod
    def test_language_is_supported_on_unsupported_lang() -> None:
        """Test ``language_is_supported`` method returns ``False`` for unsupported language."""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = cb_checker.language_is_supported("some-unsupported-lang")

        assert result is False

    @staticmethod
    def test_create_checker_returns_function() -> None:
        """Test ``create_checker`` method returns a lambda function.

        Currently unknown how to test if lambda body is ``self.check``.
        """
        cb_checker = checker.CodeBlockChecker("<string>")

        result = cb_checker.create_checker("", "")

        assert isfunction(result)
        assert result.__name__ == "<lambda>"

    @staticmethod
    def test_check_returns_none_on_unsupported_lang() -> None:
        """Test ``check`` returns ``None`` on unsupported language."""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check("", "some-unsupported-lang"))

        assert not result

    @staticmethod
    def test_check_returns_none_on_ok_code_block_for_supported_lang() -> None:
        """Test ``check`` returns ``None`` on ok code block for supported language."""
        source = """
print("rstcheck")
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check(source, "python"))

        assert not result

    @staticmethod
    @pytest.mark.skipif(sys.version_info > (3, 9), reason="Requires python3.9 or lower")
    def test_check_returns_error_on_bad_code_block_for_supported_lang_pre310() -> None:
        """Test ``check`` returns error on bad code block for supported language.

        In Python version 3.10 the error messag changed.
        """
        source = """
print(
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check(source, "python"))

        assert "unexpected EOF while parsing" in result[0]["message"]

    @staticmethod
    @pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires python3.10 or higher")
    def test_check_returns_error_on_bad_code_block_for_supported_lang() -> None:
        """Test ``check`` returns error on bad code block for supported language."""
        source = """
print(
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check(source, "python"))

        assert "'(' was never closed" in result[0]["message"]

    @staticmethod
    def test_check_python_returns_none_on_ok_code_block() -> None:
        """Test ``check_python`` returns ``None`` on ok code block."""
        source = """
print("rstcheck")
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_python(source))

        assert not result

    @staticmethod
    @pytest.mark.skipif(sys.version_info > (3, 9), reason="Requires python3.9 or lower")
    def test_check_python_returns_error_on_bad_code_block_pre310() -> None:
        """Test ``check_python`` returns error on bad code block.

        In Python version 3.10 the error messag changed.
        """
        source = """
print(
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_python(source))

        assert "unexpected EOF while parsing" in result[0]["message"]

    @staticmethod
    @pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires python3.10 or higher")
    def test_check_python_returns_error_on_bad_code_block() -> None:
        """Test ``check_python`` returns error on bad code block."""
        source = """
print(
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_python(source))

        assert "'(' was never closed" in result[0]["message"]

    @staticmethod
    def test_check_json_returns_none_on_ok_code_block() -> None:
        """Test ``check_json`` returns ``None`` on ok code block."""
        source = """
{
    "key": "value"
}
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_json(source))

        assert not result

    @staticmethod
    def test_check_json_returns_error_on_bad_code_block() -> None:
        """Test ``check_json`` returns error on bad code block."""
        source = """
{
    "key":
}
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_json(source))

        assert "Expecting value:" in result[0]["message"]

    @staticmethod
    def test_check_xml_returns_none_on_ok_code_block() -> None:
        """Test ``check_xml`` returns ``None`` on ok code block."""
        source = """<?xml version="1.0" encoding="UTF-8"?>
<note>
    <heading>Reminder</heading>
</note>
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_xml(source))

        assert not result

    @staticmethod
    def test_check_xml_returns_error_on_bad_code_block() -> None:
        """Test ``check_xml`` returns error on bad code block."""
        source = """<?xml version="1.0" encoding="UTF-8"?>
<note>
    <heading>Reminder
</note>
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_xml(source))

        assert "mismatched tag:" in result[0]["message"]

    @staticmethod
    def test_check_rst_returns_none_on_ok_code_block() -> None:
        """Test ``check_rst`` returns ``None`` on ok code block."""
        source = """
Heading
=======
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_rst(source))

        assert not result

    @staticmethod
    def test_check_rst_returns_error_on_bad_code_block() -> None:
        """Test ``check_rst`` returns error on bad code block."""
        source = """
Heading
======
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_rst(source))

        assert "Title underline too short." in result[0]["message"]

    @staticmethod
    def test_check_doctest_returns_none_on_ok_code_block() -> None:
        """Test ``check_doctest`` returns ``None`` on ok code block."""
        source = """
>>> x = 1
>>> x
1
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_doctest(source))

        assert not result

    @staticmethod
    def test_check_doctest_returns_error_on_bad_code_block() -> None:
        """Test ``check_doctest`` returns error on bad code block."""
        source = """
>>> x = 1
>>>> x
1
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_doctest(source))

        assert "lacks blank after >>>: '>>>> x'" in result[0]["message"]

    @staticmethod
    def test_check_doctest_returns_none_on_bad_code_block_if_regex_no_matching(
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test ``check_doctest`` returns ``None`` on bad code block if regex is not matching."""
        monkeypatch.setattr(checker, "DOCTEST_LINE_NO_REGEX", re.compile("bad-regex"))
        source = """
>>> x = 1
>>>> x
1
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_doctest(source))

        assert not result

    @staticmethod
    def test_check_bash_returns_none_on_ok_code_block() -> None:
        """Test ``check_bash`` returns ``None`` on ok code block."""
        source = """
if [ "$x" == 'y' ]
then
    exit 1
fi
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_bash(source))

        assert not result

    @staticmethod
    def test_check_bash_returns_error_on_bad_code_block() -> None:
        """Test ``check_bash`` returns error on bad code block."""
        source = """
{
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_bash(source))

        assert "syntax error: unexpected end of file" in result[0]["message"]

    @staticmethod
    def test_check_c_returns_none_on_ok_code_block() -> None:
        """Test ``check_c`` returns ``None`` on ok code block."""
        source = """
float foo(int n)
{
    // Test C99.
    float x[n];
    x[0] = 1;
    return x[0];
}
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_c(source))

        assert not result

    @staticmethod
    @pytest.mark.skipif(sys.platform != "linux", reason="Linux specific error message")
    def test_check_c_returns_error_on_bad_code_block_linx() -> None:
        """Test ``check_c`` returns error on bad code block."""
        source = """
int main()
{
    return x;
}
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_c(source))

        assert (
            "error: \u2018x\u2019 undeclared (first use in this function)" in result[0]["message"]
        )

    @staticmethod
    @pytest.mark.skipif(sys.platform != "darwin", reason="MacOS specific error message")
    def test_check_c_returns_error_on_bad_code_block_macos() -> None:
        """Test ``check_c`` returns error on bad code block."""
        source = """
int main()
{
    return x;
}
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_c(source))

        assert "error: use of undeclared identifier 'x'" in result[0]["message"]

    @staticmethod
    @pytest.mark.skipif(sys.platform != "win32", reason="Windows specific error message")
    def test_check_c_returns_error_on_bad_code_block_windows() -> None:
        """Test ``check_c`` returns error on bad code block."""
        source = """
int main()
{
    return x;
}
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_c(source))

        assert "ERROR" in result[0]["message"]

    @staticmethod
    def test_check_cpp_returns_none_on_ok_code_block() -> None:
        """Test ``check_cpp`` returns ``None`` on ok code block."""
        source = """
#include <iostream>

int main()
{
    auto x = 1;
    return x;
}
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_cpp(source))

        assert not result

    @staticmethod
    @pytest.mark.skipif(sys.platform != "linux", reason="Linux specific error message")
    def test_check_cpp_returns_error_on_bad_code_block_linux() -> None:
        """Test ``check_cpp`` returns error on bad code block."""
        source = """
int main()
{
    return x;
}
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_cpp(source))

        assert "error: \u2018x\u2019 was not declared in this scope" in result[0]["message"]

    @staticmethod
    @pytest.mark.skipif(sys.platform != "darwin", reason="MacOS specific error message")
    def test_check_cpp_returns_error_on_bad_code_block_macos() -> None:
        """Test ``check_cpp`` returns error on bad code block."""
        source = """
int main()
{
    return x;
}
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_cpp(source))

        assert "error: use of undeclared identifier 'x'" in result[0]["message"]

    @staticmethod
    @pytest.mark.skipif(sys.platform != "win32", reason="Windows specific error message")
    def test_check_cpp_returns_error_on_bad_code_block_windows() -> None:
        """Test ``check_cpp`` returns error on bad code block."""
        source = """
int main()
{
    return x;
}
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(cb_checker.check_cpp(source))

        assert "ERROR: \u2018x\u2019 was not declared in this scope" in result[0]["message"]

    @staticmethod
    def test__gcc_checker_returns_none_on_ok_cpp_code_block() -> None:
        """Test ``_gcc_checker`` returns ``None`` on ok c++ code block."""
        source = """
#include <iostream>

int main()
{
    auto x = 1;
    return x;
}
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(
            cb_checker._gcc_checker(  # pylint: disable=protected-access
                source, ".cpp", [os.getenv("CXX", "g++")]
            )
        )

        assert not result

    @staticmethod
    @pytest.mark.skipif(sys.platform != "linux", reason="Linux specific error message")
    def test__gcc_checker_returns_error_on_bad_cpp_code_block_linx() -> None:
        """Test ``_gcc_checker`` returns error on bad c++ code block."""
        source = """
int main()
{
    return x;
}
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(
            cb_checker._gcc_checker(  # pylint: disable=protected-access
                source, ".cpp", [os.getenv("CXX", "g++")]
            )
        )

        assert "error: \u2018x\u2019 was not declared in this scope" in result[0]["message"]

    @staticmethod
    @pytest.mark.skipif(sys.platform != "darwin", reason="MacOS specific error message")
    def test__gcc_checker_returns_error_on_bad_cpp_code_block_macos() -> None:
        """Test ``_gcc_checker`` returns error on bad c++ code block."""
        source = """
int main()
{
    return x;
}
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(
            cb_checker._gcc_checker(  # pylint: disable=protected-access
                source, ".cpp", [os.getenv("CXX", "g++")]
            )
        )

        assert "error: use of undeclared identifier 'x'" in result[0]["message"]

    @staticmethod
    @pytest.mark.skipif(sys.platform != "win32", reason="Windows specific error message")
    def test__gcc_checker_returns_error_on_bad_cpp_code_block_windows() -> None:
        """Test ``_gcc_checker`` returns error on bad c++ code block."""
        source = """
int main()
{
    return x;
}
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = list(
            cb_checker._gcc_checker(  # pylint: disable=protected-access
                source, ".cpp", [os.getenv("CXX", "g++")]
            )
        )

        assert "ERROR" in result[0]["message"]

    @staticmethod
    def test__run_in_subprocess_returns_none_on_ok_cpp_code_block() -> None:
        """Test ``_run_in_subprocess`` returns ``None`` on ok c++ code block."""
        source = """
#include <iostream>

int main()
{
    auto x = 1;
    return x;
}
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = cb_checker._run_in_subprocess(  # pylint: disable=protected-access
            source, ".cpp", [os.getenv("CXX", "g++")]
        )

        assert not result

    @staticmethod
    @pytest.mark.skipif(sys.platform != "linux", reason="Linux specific error message")
    def test__run_in_subprocess_returns_error_on_bad_cpp_code_block_linux() -> None:
        """Test ``_run_in_subprocess`` returns error on bad c++ code block."""
        source = """
int main()
{
    return x;
}
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = cb_checker._run_in_subprocess(  # pylint: disable=protected-access
            source, ".cpp", [os.getenv("CXX", "g++")]
        )

        assert result is not None
        assert "error: \u2018x\u2019 was not declared in this scope" in result[0]
        assert result[1].suffix == ".cpp"

    @staticmethod
    @pytest.mark.skipif(sys.platform != "darwin", reason="MacOS specific error message")
    def test__run_in_subprocess_returns_error_on_bad_cpp_code_block_macos() -> None:
        """Test ``_run_in_subprocess`` returns error on bad c++ code block."""
        source = """
int main()
{
    return x;
}
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = cb_checker._run_in_subprocess(  # pylint: disable=protected-access
            source, ".cpp", [os.getenv("CXX", "g++")]
        )

        assert result is not None
        assert "error: use of undeclared identifier 'x'" in result[0]
        assert result[1].suffix == ".cpp"

    @staticmethod
    @pytest.mark.skipif(sys.platform != "win32", reason="Windows specific error message")
    def test__run_in_subprocess_returns_error_on_bad_cpp_code_block_windows() -> None:
        """Test ``_run_in_subprocess`` returns error on bad c++ code block."""
        source = """
int main()
{
    return x;
}
"""
        cb_checker = checker.CodeBlockChecker("<string>")

        result = cb_checker._run_in_subprocess(  # pylint: disable=protected-access
            source, ".cpp", [os.getenv("CXX", "g++")]
        )

        assert result is not None
        assert "ERROR" in result[0]
        assert result[1].suffix == ".cpp"

    @staticmethod
    @pytest.mark.skipif(sys.platform != "linux", reason="Linux specific error message")
    def test__run_in_subprocess_returns_error_on_bad_cpp_code_block_with_filename_linux() -> None:
        """Test ``_run_in_subprocess`` returns error on bad c++ code block from filename."""
        source = """
int main()
{
    return x;
}
"""
        cb_checker = checker.CodeBlockChecker(pathlib.Path("filename.cpp"))

        result = cb_checker._run_in_subprocess(  # pylint: disable=protected-access
            source, ".cpp", [os.getenv("CXX", "g++")]
        )

        assert result is not None
        assert "error: \u2018x\u2019 was not declared in this scope" in result[0]
        assert result[1].suffix == ".cpp"

    @staticmethod
    @pytest.mark.skipif(sys.platform != "darwin", reason="MacOS specific error message")
    def test__run_in_subprocess_returns_error_on_bad_cpp_code_block_with_filename_macos() -> None:
        """Test ``_run_in_subprocess`` returns error on bad c++ code block from filename."""
        source = """
int main()
{
    return x;
}
"""
        cb_checker = checker.CodeBlockChecker(pathlib.Path("filename.cpp"))

        result = cb_checker._run_in_subprocess(  # pylint: disable=protected-access
            source, ".cpp", [os.getenv("CXX", "g++")]
        )

        assert result is not None
        assert "error: use of undeclared identifier 'x'" in result[0]
        assert result[1].suffix == ".cpp"

    @staticmethod
    @pytest.mark.skipif(sys.platform != "win32", reason="Windows specific error message")
    def test__run_in_subprocess_returns_error_on_bad_cpp_code_block_with_filename_windows() -> None:
        """Test ``_run_in_subprocess`` returns error on bad c++ code block from filename."""
        source = """
int main()
{
    return x;
}
"""
        cb_checker = checker.CodeBlockChecker(pathlib.Path("filename.cpp"))

        result = cb_checker._run_in_subprocess(  # pylint: disable=protected-access
            source, ".cpp", [os.getenv("CXX", "g++")]
        )

        assert result is not None
        assert "ERROR" in result[0]
        assert result[1].suffix == ".cpp"

    @staticmethod
    def test__parse_gcc_style_error_message_raises_on_bad_format() -> None:
        """Test ``_parse_gcc_style_error_message`` method raises ``ValueError`` on bad format."""
        message = "Foo bar"

        with pytest.raises(ValueError, match="Message cannot be parsed."):
            checker._parse_gcc_style_error_message(  # pylint: disable=protected-access
                message, "<string>"
            )

    @staticmethod
    def test__parse_gcc_style_error_message_with_column() -> None:
        """Test ``_parse_gcc_style_error_message`` method with column."""
        message = "<string>:16:32: Error message"
        error = types.LintError(
            source_origin="<string>",
            line_number=16,
            message="Error message",
        )

        result = checker._parse_gcc_style_error_message(  # pylint: disable=protected-access
            message, "<string>"
        )

        assert result == error

    @staticmethod
    def test__parse_gcc_style_error_message_without_column() -> None:
        """Test ``_parse_gcc_style_error_message`` method without column."""
        message = "<string>:16: Error message"
        error = types.LintError(
            source_origin="<string>",
            line_number=16,
            message="Error message",
        )

        result = checker._parse_gcc_style_error_message(  # pylint: disable=protected-access
            message, "<string>", False
        )

        assert result == error
