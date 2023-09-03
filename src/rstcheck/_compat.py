"""Compatability code for older python version."""
from __future__ import annotations

try:
    from importlib.metadata import version
except ImportError:  # pragma: py-gte-38
    from importlib_metadata import version  # type: ignore[import,no-redef]


__all__ = ["version"]
