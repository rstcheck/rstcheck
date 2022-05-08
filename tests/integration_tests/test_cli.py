"""Integration test for the CLI."""
import pathlib

import pytest
import typer
import typer.testing

from rstcheck import _extras
from tests.conftest import EXAMPLES_DIR, TESTING_DIR
from tests.integration_tests.conftest import ERROR_CODE_REGEX


def test_cli_help_message(cli_app: typer.Typer, cli_runner: typer.testing.CliRunner) -> None:
    """Test help message."""
    result = cli_runner.invoke(cli_app, "--help")

    assert result.exit_code == 0
    assert "Enabled features:" in result.stdout


@pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
def test_cli_help_message_with_sphinx(
    cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
) -> None:
    """Test help message when sphinx is installed."""
    result = cli_runner.invoke(cli_app, "--help")

    assert result.exit_code == 0
    assert "Enabled features:" in result.stdout
    assert "Sphinx" in result.stdout


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


def test_all_good_examples_recurively(
    cli_app: typer.Typer,
    cli_runner: typer.testing.CliRunner,
) -> None:
    """Test all files in ``testing/examples/good`` recursively."""
    test_dir = EXAMPLES_DIR / "good"

    result = cli_runner.invoke(cli_app, [str(test_dir), "--recursive"])

    assert result.exit_code == 0
    assert "Success! No issues detected." in result.stdout


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


def test_all_bad_examples_recurively(
    cli_app: typer.Typer,
    cli_runner: typer.testing.CliRunner,
) -> None:
    """Test all files in ``testing/examples/bad`` recursively."""
    test_dir = EXAMPLES_DIR / "bad"

    result = cli_runner.invoke(cli_app, [str(test_dir), "--recursive"])

    assert result.exit_code != 0
    assert ERROR_CODE_REGEX.search(result.stdout) is not None


def test_mix_of_good_and_bad_examples(
    cli_app: typer.Typer,
    cli_runner: typer.testing.CliRunner,
) -> None:
    """Test mix of good and bad examples."""
    test_file_good = EXAMPLES_DIR / "good" / "code_blocks.rst"
    test_file_bad = EXAMPLES_DIR / "bad" / "rst.rst"

    result = cli_runner.invoke(cli_app, [str(test_file_good), str(test_file_bad)])

    assert result.exit_code != 0
    assert len(ERROR_CODE_REGEX.findall(result.stdout)) == 1


def test_good_example_with_piping(
    cli_app: typer.Typer,
    cli_runner: typer.testing.CliRunner,
) -> None:
    """Test good example file piped into rstcheck."""
    test_file = EXAMPLES_DIR / "good" / "code_blocks.rst"
    test_file_content = test_file.read_text("utf-8")

    result = cli_runner.invoke(cli_app, "-", input=test_file_content)

    assert result.exit_code == 0


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


def test_piping_is_not_allowed_with_additional_files(cli_app: typer.Typer) -> None:
    """Test piping into rstcheck is not allowed with additional files.

    Test cli prints error to stderr.
    """
    cli_runner_divided_output = typer.testing.CliRunner(mix_stderr=False)

    result = cli_runner_divided_output.invoke(cli_app, ["-", "foo"])

    assert result.exit_code == 1
    assert "'-' is only allowed without additional files." in result.stderr
    assert "Aborted!" in result.stderr


def test_without_report_exits_zero(
    cli_app: typer.Typer,
    cli_runner: typer.testing.CliRunner,
) -> None:
    """Test bad example without report is ok."""
    test_file = EXAMPLES_DIR / "bad" / "rst.rst"

    result = cli_runner.invoke(cli_app, [str(test_file), "--report-level", "none"])

    assert result.exit_code == 0


def test_matching_ignore_msg_exits_zero(
    cli_app: typer.Typer,
    cli_runner: typer.testing.CliRunner,
) -> None:
    """Test matching ignore message."""
    test_file = EXAMPLES_DIR / "bad" / "rst.rst"

    result = cli_runner.invoke(
        cli_app, [str(test_file), "--ignore-messages", r"(Title .verline & underline mismatch\.$)"]
    )

    assert result.exit_code == 0


def test_non_matching_ignore_msg_errors(
    cli_app: typer.Typer,
    cli_runner: typer.testing.CliRunner,
) -> None:
    """Test non matching ignore message."""
    test_file = EXAMPLES_DIR / "bad" / "rst.rst"

    result = cli_runner.invoke(cli_app, [str(test_file), "--ignore-messages", r"(No match\.$)"])

    assert result.exit_code != 0


def test_custom_directive_and_role(
    cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
) -> None:
    """Test file with custom directive and role."""
    test_file = EXAMPLES_DIR / "custom" / "custom_directive_and_role.rst"

    result = cli_runner.invoke(cli_app, str(test_file))

    assert result.exit_code != 0
    assert len(ERROR_CODE_REGEX.findall(result.stdout)) == 4


def test_custom_directive_and_role_with_ignore(
    cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
) -> None:
    """Test file with custom directive and role and CLI ignores."""
    test_file = EXAMPLES_DIR / "custom" / "custom_directive_and_role.rst"

    result = cli_runner.invoke(
        cli_app,
        [
            "--ignore-directives",
            "my-directive",
            "--ignore-roles",
            "some-custom-thing",
            str(test_file),
        ],
    )

    assert result.exit_code == 0
    assert "Success! No issues detected." in result.stdout


def test_custom_directive_and_role_with_config_file(
    cli_app: typer.Typer, cli_runner: typer.testing.CliRunner
) -> None:
    """Test file with custom directive and role and config file."""
    test_file = EXAMPLES_DIR / "custom" / "custom_directive_and_role.rst"
    config_file = EXAMPLES_DIR / "custom" / "rstcheck.custom.ini"

    result = cli_runner.invoke(cli_app, ["--config", str(config_file), str(test_file)])

    assert result.exit_code == 0
    assert "Success! No issues detected." in result.stdout
