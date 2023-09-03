"""Compatability code for older python version."""
from __future__ import annotations

try:
    from importlib.metadata import version
except ImportError:  # pragma: py-gte-38
    from importlib_metadata import version  # type: ignore[import,no-redef]


try:
    from typing import Literal
except ImportError:  # pragma: py-gte-38
    from typing import Literal  # type: ignore[assignment]


__all__ = ["Literal", "version"]
