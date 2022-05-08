"""Integration test for the CLI."""
import pathlib

import pytest
import typer
import typer.testing

from tests.conftest import EXAMPLES_DIR, TESTING_DIR
from tests.integration_tests.conftest import ERROR_CODE_REGEX


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
    assert ERROR_CODE_REGEX.search(result.stdout) is None


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
    assert "Success! No issues detected." not in result.stdout


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

    result = cli_runner.invoke(
        cli_app, ["--recursive", "--config", str(config_file), str(test_file)]
    )

    assert "Success! No issues detected." in result.stdout
    assert result.exit_code == 0
