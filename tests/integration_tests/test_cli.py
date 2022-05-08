"""Integration test for the CLI."""
import pathlib

import pytest
import typer
import typer.testing

from tests.conftest import TESTING_DIR
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
