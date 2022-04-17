"""Testing utility."""
import typing

import pytest

import rstcheck


@pytest.fixture(name="enable_sphinx_if_possible", scope="module")
def _enable_sphinx_if_possible_fixture() -> typing.Generator[None, None, None]:
    """Enable sphinx for tests if possible."""
    with rstcheck.enable_sphinx_if_possible():
        yield
