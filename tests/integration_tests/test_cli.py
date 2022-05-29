"""Integration test for the CLI."""
import pathlib
import re
import sys

import pytest
import typer
import typer.testing
from rstcheck_core import _extras

from tests.conftest import EXAMPLES_DIR, TESTING_DIR
from tests.integration_tests.conftest import ERROR_CODE_REGEX


def test_exit_0_on_nonexisting_config_path(
    cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
) -> None:
    """Test runner exits with error on non existing config path."""
    test_file = EXAMPLES_DIR / "good" / "rst.rst"
    config_file = pathlib.Path("does-not-exist")

    result = cli_runner.invoke(cli_app, [str(test_file), "--config", str(config_file)])

    assert result.exit_code != 0


class TestHelpMessage:
    """Test help CLI messages."""

    @staticmethod
    def test_cli_version_message(cli_app: typer.Typer, cli_runner: typer.testing.CliRunner) -> None:
        """Test help message."""
        result = cli_runner.invoke(cli_app, "--version")

        assert result.exit_code == 0
        assert "rstcheck CLI Version:" in result.stdout
        assert "rstcheck-core Version:" in result.stdout

    @staticmethod
    def test_cli_help_message(cli_app: typer.Typer, cli_runner: typer.testing.CliRunner) -> None:
        """Test help message."""
        result = cli_runner.invoke(cli_app, "--help")

        assert result.exit_code == 0
        assert "Enabled features:" in result.stdout

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    def test_cli_help_message_with_sphinx(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test help message when sphinx is installed."""
        result = cli_runner.invoke(cli_app, "--help")

        assert result.exit_code == 0
        assert "Enabled features:" in result.stdout
        assert "Sphinx" in result.stdout

    @staticmethod
    @pytest.mark.skipif(not _extras.TOMLI_INSTALLED, reason="Depends on toml extra.")
    def test_cli_help_message_with_tomli(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test help message when toml is installed."""
        result = cli_runner.invoke(cli_app, "--help")

        assert result.exit_code == 0
        assert "pyproject.toml" in result.stdout
        assert "Enabled features:" in result.stdout
        assert "Toml" in result.stdout


class TestInput:
    """Test file input with good and bad files and piping."""

    @staticmethod
    @pytest.mark.parametrize("test_file", list(TESTING_DIR.glob("examples/good/*.rst")))
    def test_all_good_examples(
        test_file: pathlib.Path,
        cli_app: typer.Typer,
        cli_runner: typer.testing.CliRunner,
    ) -> None:
        """Test all files in ``testing/examples/good`` are errorless."""
        result = cli_runner.invoke(cli_app, str(test_file))

        assert result.exit_code == 0
        assert "Success! No issues detected." in result.stdout

    @staticmethod
    @pytest.mark.skipif(
        sys.platform == "win32", reason="Unknown Windows specific wrong negative. `assert 1 != 0`"
    )
    def test_all_good_examples_recurively(
        cli_app: typer.Typer,
        cli_runner: typer.testing.CliRunner,
    ) -> None:
        """Test all files in ``testing/examples/good`` recursively."""
        test_dir = EXAMPLES_DIR / "good"

        result = cli_runner.invoke(cli_app, [str(test_dir), "--recursive"])

        assert result.exit_code == 0
        assert "Success! No issues detected." in result.stdout

    @staticmethod
    @pytest.mark.skipif(
        sys.platform == "win32", reason="Unknown Windows specific wrong positive. `assert 0 != 0`"
    )
    @pytest.mark.parametrize("test_file", list(TESTING_DIR.glob("examples/bad/*.rst")))
    def test_all_bad_examples(
        test_file: pathlib.Path,
        cli_app: typer.Typer,
        cli_runner: typer.testing.CliRunner,
    ) -> None:
        """Test all files in ``testing/examples/bad`` have errors."""
        result = cli_runner.invoke(cli_app, str(test_file))

        assert result.exit_code != 0
        assert ERROR_CODE_REGEX.search(result.stdout) is not None

    @staticmethod
    def test_all_bad_examples_recurively(
        cli_app: typer.Typer,
        cli_runner: typer.testing.CliRunner,
    ) -> None:
        """Test all files in ``testing/examples/bad`` recursively."""
        test_dir = EXAMPLES_DIR / "bad"

        result = cli_runner.invoke(cli_app, [str(test_dir), "--recursive"])

        assert result.exit_code != 0
        assert ERROR_CODE_REGEX.search(result.stdout) is not None

    @staticmethod
    def test_mix_of_good_and_bad_examples(
        cli_app: typer.Typer,
        cli_runner: typer.testing.CliRunner,
    ) -> None:
        """Test mix of good and bad examples."""
        test_file_good = EXAMPLES_DIR / "good" / "rst.rst"
        test_file_bad = EXAMPLES_DIR / "bad" / "rst.rst"

        result = cli_runner.invoke(cli_app, [str(test_file_good), str(test_file_bad)])

        assert result.exit_code != 0
        assert len(ERROR_CODE_REGEX.findall(result.stdout)) == 1

    @staticmethod
    def test_good_example_with_piping(
        cli_app: typer.Typer,
        cli_runner: typer.testing.CliRunner,
    ) -> None:
        """Test good example file piped into rstcheck."""
        test_file = EXAMPLES_DIR / "good" / "rst.rst"
        test_file_content = test_file.read_text("utf-8")

        result = cli_runner.invoke(cli_app, "-", input=test_file_content)

        assert result.exit_code == 0

    @staticmethod
    def test_bad_example_with_piping(
        cli_app: typer.Typer,
        cli_runner: typer.testing.CliRunner,
    ) -> None:
        """Test bad example file piped into rstcheck."""
        test_file = EXAMPLES_DIR / "bad" / "rst.rst"
        test_file_content = test_file.read_text("utf-8")

        result = cli_runner.invoke(cli_app, "-", input=test_file_content)

        assert result.exit_code != 0
        assert len(ERROR_CODE_REGEX.findall(result.stdout)) == 1

    @staticmethod
    def test_piping_is_not_allowed_with_additional_files(cli_app: typer.Typer) -> None:
        """Test piping into rstcheck is not allowed with additional files.

        Test cli prints error to stderr.
        """
        cli_runner_divided_output = typer.testing.CliRunner(mix_stderr=False)

        result = cli_runner_divided_output.invoke(cli_app, ["-", "foo"])

        assert result.exit_code == 1
        assert "'-' is only allowed without additional files." in result.stderr
        assert "Aborted!" in result.stderr


class TestIgnoreOptions:
    """Test --ignore-* options and --report-level."""

    @staticmethod
    def test_without_report_exits_zero(
        cli_app: typer.Typer,
        cli_runner: typer.testing.CliRunner,
    ) -> None:
        """Test bad example without report is ok."""
        test_file = EXAMPLES_DIR / "bad" / "rst.rst"

        result = cli_runner.invoke(cli_app, [str(test_file), "--report-level", "none"])

        assert result.exit_code == 0

    @staticmethod
    def test_ignore_language_silences_error(
        cli_app: typer.Typer,
        cli_runner: typer.testing.CliRunner,
    ) -> None:
        """Test bad example with ignored language is ok."""
        test_file = EXAMPLES_DIR / "bad" / "cpp.rst"

        result = cli_runner.invoke(cli_app, [str(test_file), "--ignore-languages", "cpp"])

        assert result.exit_code == 0

    @staticmethod
    def test_matching_ignore_msg_exits_zero(
        cli_app: typer.Typer,
        cli_runner: typer.testing.CliRunner,
    ) -> None:
        """Test matching ignore message."""
        test_file = EXAMPLES_DIR / "bad" / "rst.rst"

        result = cli_runner.invoke(
            cli_app,
            [str(test_file), "--ignore-messages", r"(Title .verline & underline mismatch\.$)"],
        )

        assert result.exit_code == 0

    @staticmethod
    def test_non_matching_ignore_msg_errors(
        cli_app: typer.Typer,
        cli_runner: typer.testing.CliRunner,
    ) -> None:
        """Test non matching ignore message."""
        test_file = EXAMPLES_DIR / "bad" / "rst.rst"

        result = cli_runner.invoke(cli_app, [str(test_file), "--ignore-messages", r"(No match\.$)"])

        assert result.exit_code != 0

    @staticmethod
    def test_table_substitution_error_fixed_by_ignore(
        cli_app: typer.Typer,
        cli_runner: typer.testing.CliRunner,
    ) -> None:
        """Test that ignored substitutions in tables are correctly handled."""
        test_file = EXAMPLES_DIR / "bad" / "table_substitutions.rst"

        result = cli_runner.invoke(
            cli_app, [str(test_file), "--ignore-substitutions", "FOO_ID,BAR_ID"]
        )

        assert result.exit_code == 0


class TestWithoutConfigFile:
    """Test without config file in dir tree."""

    @staticmethod
    @pytest.mark.skipif(
        sys.platform == "win32", reason="Unknown Windows specific wrong positive. `assert 0 != 0`"
    )
    @pytest.mark.skipif(sys.platform == "darwin", reason="MacOS specific variant exists")
    def test_error_without_config_file(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test bad example without set config file and implicit config file shows errors."""
        test_file = EXAMPLES_DIR / "without_configuration" / "bad.rst"

        result = cli_runner.invoke(cli_app, str(test_file))

        assert result.exit_code != 0
        assert len(ERROR_CODE_REGEX.findall(result.stdout)) == 6

    @staticmethod
    @pytest.mark.skipif(sys.platform != "darwin", reason="MacOS specific error count")
    def test_error_without_config_file_macos(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test bad example without set config file and implicit config file shows errors.

        On MacOS the cpp code block generates an additional error compared to linux:
        ``(ERROR/3) (cpp) warning: no newline at end of file [-Wnewline-eof]``
        """
        test_file = EXAMPLES_DIR / "without_configuration" / "bad.rst"

        result = cli_runner.invoke(cli_app, str(test_file))

        assert result.exit_code != 0
        assert len(ERROR_CODE_REGEX.findall(result.stdout)) == 7

    @staticmethod
    def test_no_error_with_set_ini_config_file(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test bad example with set INI config file does not error."""
        test_file = EXAMPLES_DIR / "without_configuration" / "bad.rst"
        config_file = EXAMPLES_DIR / "with_configuration" / "rstcheck.ini"

        result = cli_runner.invoke(cli_app, [str(test_file), "--config", str(config_file)])

        assert result.exit_code == 0

    @staticmethod
    def test_no_error_with_set_config_dir(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test bad example with set config dir does not error."""
        test_file = EXAMPLES_DIR / "without_configuration" / "bad.rst"
        config_dir = EXAMPLES_DIR / "with_configuration"

        result = cli_runner.invoke(cli_app, [str(test_file), "--config", str(config_dir)])

        assert result.exit_code == 0

    @staticmethod
    @pytest.mark.skipif(not _extras.TOMLI_INSTALLED, reason="Depends on toml extra.")
    def test_no_error_with_set_toml_config_file(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test bad example with set TOML config file does not error."""
        test_file = EXAMPLES_DIR / "without_configuration" / "bad.rst"
        config_file = EXAMPLES_DIR / "with_configuration" / "pyproject.toml"

        result = cli_runner.invoke(cli_app, [str(test_file), "--config", str(config_file)])

        assert result.exit_code == 0


class TestWithConfigFile:
    """Test with config file in dir tree."""

    @staticmethod
    @pytest.mark.skipif(sys.platform == "darwin", reason="MacOS specific variant exists")
    def test_file_1_is_bad_without_config(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test bad file ``bad.rst`` without config file is not ok."""
        test_file = EXAMPLES_DIR / "with_configuration" / "bad.rst"
        config_file = pathlib.Path("NONE")

        result = cli_runner.invoke(cli_app, [str(test_file), "--config", str(config_file)])

        assert result.exit_code != 0
        assert len(ERROR_CODE_REGEX.findall(result.stdout)) == 6

    @staticmethod
    @pytest.mark.skipif(sys.platform != "darwin", reason="MacOS specific error count")
    def test_file_1_is_bad_without_config_macos(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test bad file ``bad.rst`` without config file is not ok.

        On MacOS the cpp code block generates an additional error compared to linux:
        ``(ERROR/3) (cpp) warning: no newline at end of file [-Wnewline-eof]``
        """
        test_file = EXAMPLES_DIR / "with_configuration" / "bad.rst"
        config_file = pathlib.Path("NONE")

        result = cli_runner.invoke(cli_app, [str(test_file), "--config", str(config_file)])

        assert result.exit_code != 0
        assert len(ERROR_CODE_REGEX.findall(result.stdout)) == 7

    @staticmethod
    def test_file_2_is_bad_without_config(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test bad file ``bad_rst.rst`` without config file not ok."""
        test_file = EXAMPLES_DIR / "with_configuration" / "bad_rst.rst"
        config_file = pathlib.Path("NONE")

        result = cli_runner.invoke(cli_app, [str(test_file), "--config", str(config_file)])

        assert result.exit_code != 0
        assert len(ERROR_CODE_REGEX.findall(result.stdout)) == 2

    @staticmethod
    def test_bad_file_1_with_implicit_config_no_errors(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test bad file ``bad.rst`` with implicit config file is ok."""
        test_file = EXAMPLES_DIR / "with_configuration" / "bad.rst"

        result = cli_runner.invoke(cli_app, str(test_file))

        assert result.exit_code == 0

    @staticmethod
    @pytest.mark.skipif(
        sys.platform == "win32", reason="Unknown Windows specific wrong positive. `assert 0 != 0`"
    )
    def test_bad_file_2_with_implicit_config_some_errors(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test bad file ``bad_rst.rst`` with implicit config file partially ok."""
        test_file = EXAMPLES_DIR / "with_configuration" / "bad_rst.rst"

        result = cli_runner.invoke(cli_app, str(test_file))

        assert result.exit_code != 0
        assert len(ERROR_CODE_REGEX.findall(result.stdout)) == 1

    @staticmethod
    def test_bad_file_1_with_explicit_config_no_errors(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test bad file ``bad.rst`` with explicit config file is ok."""
        test_file = EXAMPLES_DIR / "with_configuration" / "bad.rst"
        config_file = EXAMPLES_DIR / "with_configuration" / "rstcheck.ini"

        result = cli_runner.invoke(cli_app, [str(test_file), "--config", str(config_file)])

        assert result.exit_code == 0

    @staticmethod
    def test_bad_file_2_with_explicit_config_some_errors(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test bad file ``bad_rst.rst`` with explicit config file partially ok."""
        test_file = EXAMPLES_DIR / "with_configuration" / "bad_rst.rst"
        config_file = EXAMPLES_DIR / "with_configuration" / "rstcheck.ini"

        result = cli_runner.invoke(cli_app, [str(test_file), "--config", str(config_file)])

        assert result.exit_code != 0
        assert len(ERROR_CODE_REGEX.findall(result.stdout)) == 1


class TestWarningOnUnknownSettings:
    """Test warnings logged on unknown settings in config files."""

    @staticmethod
    @pytest.mark.parametrize("config_file_name", ["bad_config.cfg", "bad_config.toml"])
    def test_no_warnings_are_logged_by_default(
        config_file_name: str,
        cli_app: typer.Typer,
        cli_runner: typer.testing.CliRunner,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that no warning is logged on unknown setting by default."""
        test_file = EXAMPLES_DIR / "good" / "rst.rst"
        config_file = EXAMPLES_DIR / "with_configuration" / config_file_name

        result = cli_runner.invoke(cli_app, [str(test_file), "--config", str(config_file)])

        assert result.exit_code == 0
        assert "Unknown setting(s)" not in caplog.text

    @staticmethod
    @pytest.mark.parametrize("config_file_name", ["bad_config.cfg", "bad_config.toml"])
    def test_no_warnings_are_logged_by_default_on_ini_files(
        config_file_name: str,
        cli_app: typer.Typer,
        cli_runner: typer.testing.CliRunner,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that a warning is logged on unknown setting when activated."""
        test_file = EXAMPLES_DIR / "good" / "rst.rst"
        config_file = EXAMPLES_DIR / "with_configuration" / config_file_name

        result = cli_runner.invoke(
            cli_app, [str(test_file), "--config", str(config_file), "--warn-unknown-settings"]
        )

        assert result.exit_code == 0
        assert "Unknown setting(s)" in caplog.text


class TestCustomDirectivesAndRoles:
    """Test custom directives and roles."""

    @staticmethod
    @pytest.mark.skipif(
        sys.platform == "win32", reason="Unknown Windows specific wrong positive. `assert 0 != 0`"
    )
    def test_custom_directive_and_role(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test file with custom directive and role."""
        test_file = EXAMPLES_DIR / "custom" / "custom_directive_and_role.rst"

        result = cli_runner.invoke(cli_app, str(test_file))

        assert result.exit_code != 0
        assert len(ERROR_CODE_REGEX.findall(result.stdout)) == 4

    @staticmethod
    def test_custom_directive_and_role_with_ignore(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test file with custom directive and role and CLI ignores."""
        test_file = EXAMPLES_DIR / "custom" / "custom_directive_and_role.rst"

        result = cli_runner.invoke(
            cli_app,
            [
                "--ignore-directives",
                "custom-directive",
                "--ignore-roles",
                "custom-role",
                str(test_file),
            ],
        )

        assert result.exit_code == 0
        assert "Success! No issues detected." in result.stdout

    @staticmethod
    def test_custom_directive_and_role_with_config_file(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test file with custom directive and role and config file."""
        test_file = EXAMPLES_DIR / "custom" / "custom_directive_and_role.rst"
        config_file = EXAMPLES_DIR / "custom" / "rstcheck.custom.ini"

        result = cli_runner.invoke(cli_app, ["--config", str(config_file), str(test_file)])

        assert result.exit_code == 0
        assert "Success! No issues detected." in result.stdout


class TestSphinx:
    """Test integration with sphinx."""

    @staticmethod
    @pytest.mark.skipif(
        sys.platform == "win32", reason="Unknown Windows specific wrong positive. `assert 0 != 0`"
    )
    @pytest.mark.skipif(_extras.SPHINX_INSTALLED, reason="Test without sphinx extra.")
    def test_sphinx_role_erros_without_sphinx(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test sphinx example errors without sphinx."""
        test_file = EXAMPLES_DIR / "sphinx" / "good.rst"

        result = cli_runner.invoke(cli_app, str(test_file))

        assert result.exit_code != 0

    @staticmethod
    @pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
    def test_sphinx_role_exits_zero_with_sphinx(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test sphinx example does not error with sphinx."""
        test_file = EXAMPLES_DIR / "sphinx" / "good.rst"

        result = cli_runner.invoke(cli_app, str(test_file))

        assert result.exit_code == 0


class TestInlineIgnoreComments:
    """Test inline config comments to ignore things."""

    @staticmethod
    @pytest.mark.skipif(
        sys.platform == "win32", reason="Unknown Windows specific wrong positive. `assert 0 != 0`"
    )
    def test_bad_example_has_issues(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test all issues are found on bad example."""
        test_file = EXAMPLES_DIR / "inline_config" / "without_inline_ignore.rst"

        result = cli_runner.invoke(cli_app, str(test_file))

        assert result.exit_code != 0
        assert "custom-directive" in result.stdout
        assert "custom-role" in result.stdout
        assert "python" in result.stdout
        assert "unmatched-substitution" in result.stdout

    @staticmethod
    def test_sphinx_role_exits_zero_with_sphinx(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test no issues are found on bad example with ignore comments."""
        test_file = EXAMPLES_DIR / "sphinx" / "with_inline_ignore.rst"

        result = cli_runner.invoke(cli_app, str(test_file))

        assert result.exit_code == 0


class TestInlineFlowControlComments:
    """Test inline flow control comments to e.g. skip things."""

    @staticmethod
    @pytest.mark.skipif(
        sys.platform == "win32", reason="Unknown Windows specific wrong positive. `assert 0 != 0`"
    )
    @pytest.mark.skipif(sys.version_info[0:2] > (3, 9), reason="Requires python3.9 or lower")
    def test_bad_example_has_only_one_issue_pre310(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test only one issue is detected for two same code-blocks.

        One code-block has skip comment.
        """
        test_file = EXAMPLES_DIR / "inline_config" / "with_inline_skip_code_block.rst"

        result = cli_runner.invoke(cli_app, str(test_file))

        assert result.exit_code != 0
        assert len(re.findall(r"unexpected EOF while parsing", result.stdout)) == 1

    @staticmethod
    @pytest.mark.skipif(
        sys.platform == "win32", reason="Unknown Windows specific wrong positive. `assert 0 != 0`"
    )
    @pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires python3.10 or higher")
    def test_bad_example_has_only_one_issue(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test only one issue is detected for two same code-blocks.

        One code-block has skip comment.
        """
        test_file = EXAMPLES_DIR / "inline_config" / "with_inline_skip_code_block.rst"

        result = cli_runner.invoke(cli_app, str(test_file))

        assert result.exit_code != 0
        assert len(re.findall(r"'\(' was never closed", result.stdout)) == 1

    @staticmethod
    @pytest.mark.skipif(
        sys.platform == "win32", reason="Unknown Windows specific wrong positive. `assert 0 != 0`"
    )
    @pytest.mark.skipif(sys.version_info[0:2] > (3, 9), reason="Requires python3.9 or lower")
    def test_nested_bad_example_has_only_one_issue_pre310(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test only one issue is detected for two same nested code-blocks.

        One code-block has skip comment.
        """
        test_file = EXAMPLES_DIR / "inline_config" / "with_nested_inline_skip_code_block.rst"

        result = cli_runner.invoke(cli_app, str(test_file))

        assert result.exit_code != 0
        assert len(re.findall(r"unexpected EOF while parsing", result.stdout)) == 1

    @staticmethod
    @pytest.mark.skipif(
        sys.platform == "win32", reason="Unknown Windows specific wrong positive. `assert 0 != 0`"
    )
    @pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires python3.10 or higher")
    def test_nested_bad_example_has_only_one_issue(
        cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
    ) -> None:
        """Test only one issue is detected for two same nested code-blocks.

        One code-block has skip comment.
        """
        test_file = EXAMPLES_DIR / "inline_config" / "with_nested_inline_skip_code_block.rst"

        result = cli_runner.invoke(cli_app, str(test_file))

        assert result.exit_code != 0
        assert len(re.findall(r"'\(' was never closed", result.stdout)) == 1
