"""Fixtures for integration tests."""
import pytest
import typer
import typer.testing

from rstcheck import cli


@pytest.fixture(name="cli_app")
def cli_app_fixture() -> typer.Typer:
    """Create typer app from ``cli`` function for testing."""
    app = typer.Typer()
    app.command()(cli.cli)
    return app


@pytest.fixture(name="cli_runner")
def cli_runner_fixture() -> typer.testing.CliRunner:
    """Create CLI Test Runner."""
    return typer.testing.CliRunner()
