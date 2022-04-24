"""Compatability code for older python version."""

try:
    from importlib.metadata import metadata
except ImportError:  # pragma: py-gte-38
    from importlib_metadata import metadata  # type: ignore[misc]

try:
    from typing import Literal
except ImportError:  # pragma: py-gte-38
    from typing_extensions import Literal  # type: ignore[misc]

try:
    from typing import TypedDict
except ImportError:  # pragma: py-gte-38
    from typing_extensions import TypedDict


__all__ = ["metadata", "Literal", "TypedDict"]
