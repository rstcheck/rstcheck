"""Compatability code for older python version."""

try:
    from importlib.metadata import metadata
except ModuleNotFoundError:  # pragma: py-gte-38
    from importlib_metadata import metadata  # type: ignore[misc]

try:
    from typing import Literal
except ModuleNotFoundError:  # pragma: py-gte-38
    from typing_extensions import Literal  # type: ignore[misc]

try:
    from typing import TypedDict
except ModuleNotFoundError:  # pragma: py-gte-38
    from typing_extensions import TypedDict


__all__ = ["metadata", "Literal", "TypedDict"]
