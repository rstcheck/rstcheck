"""Tests for ``cli`` module.

``cli.cli`` is not really good testable with unit tests.
Therfore here only the help message is checked with integration testing style.
Furthers tests are in the ``integration_tests`` directory.
"""
import pytest
import typer
import typer.testing

from rstcheck import _extras, cli


app = typer.Typer()
app.command()(cli.cli)

cli_runner = typer.testing.CliRunner()


def test_cli_help_message() -> None:
    """Test help message."""
    result = cli_runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Enabled features:" in result.stdout


@pytest.mark.skipif(not _extras.SPHINX_INSTALLED, reason="Depends on sphinx extra.")
def test_cli_help_message_with_sphinx() -> None:
    """Test help message when sphinx is installed."""
    result = cli_runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Enabled features:" in result.stdout
    assert "Sphinx" in result.stdout


@pytest.mark.skipif(not _extras.TOMLI_INSTALLED, reason="Depends on toml extra.")
def test_cli_help_message_with_tomli() -> None:
    """Test help message when toml is installed."""
    result = cli_runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "pyproject.toml" in result.stdout
    assert "Enabled features:" in result.stdout
    assert "Toml" in result.stdout