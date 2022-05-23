"""Compatability code for older python version."""

try:
    from importlib.metadata import version
except ImportError:  # pragma: py-gte-38
    from importlib_metadata import version

try:
    from typing import Literal
except ImportError:  # pragma: py-gte-38
    from typing_extensions import Literal  # type: ignore[misc]

try:
    from typing import Protocol
except ImportError:  # pragma: py-gte-38
    from typing_extensions import Protocol  # type: ignore[misc]

try:
    from typing import TypedDict
except ImportError:  # pragma: py-gte-38
    from typing_extensions import TypedDict


__all__ = ["Literal", "Protocol", "TypedDict", "version"]
