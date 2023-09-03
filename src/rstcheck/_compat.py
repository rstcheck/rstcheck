"""Compatability code for older python version."""

try:
    from importlib.metadata import version
except ImportError:  # pragma: py-gte-38
    from importlib_metadata import version  # type: ignore[import,no-redef]


try:
    from typing import Literal
except ImportError:  # pragma: py-gte-38
    from typing_extensions import Literal  # type: ignore[assignment]


__all__ = ["Literal", "version"]
