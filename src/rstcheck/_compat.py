"""Compatability code for older python version."""

try:
    from typing import Literal
except ImportError:  # pragma: py-gte-38
    from typing_extensions import Literal  # type: ignore[misc]


__all__ = ["Literal"]
