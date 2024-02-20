"""Tests for ``_cli`` module.

``_cli.cli`` is not really good testable with unit tests.
Therfore tests are in the ``integration_tests`` directory.
"""

from __future__ import annotations

import pytest

from rstcheck import _cli


@pytest.mark.parametrize("level", ["SEVERE", "NONE"])
def test_setup_logger_errors_on_invalid_levels(level: str) -> None:
    """Tests exception is raised on invalid levels."""
    with pytest.raises(TypeError, match=f"Invalid log level: {level}"):
        _cli.setup_logger(level)


@pytest.mark.parametrize("level", ["debug", "InFO", "WARNING", "ErRor", "critical"])
def test_setup_logger_valid_levels(level: str) -> None:
    """Test no execption is raised on valid levels."""
    _cli.setup_logger(level)  # act
