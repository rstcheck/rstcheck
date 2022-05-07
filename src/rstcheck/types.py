"""Helper types."""
import pathlib
import typing

from . import _compat


SourceFileOrString = typing.Union[pathlib.Path, _compat.Literal["<string>"]]
"""Path to source file or if it is a string then '<string>'."""


class LintError(_compat.TypedDict):
    """Dict with information about an linting error."""

    source_origin: SourceFileOrString
    line_number: int
    message: str


YieldedLintError = typing.Generator[LintError, None, None]
"""Yielded version of type ``LintError``."""


class IgnoreDict(_compat.TypedDict):
    """Dict with ignore information."""

    # NOTE: Pattern type-arg errors pydanic: https://github.com/samuelcolvin/pydantic/issues/2636
    messages: typing.Optional[typing.Pattern]  # type: ignore[type-arg]
    languages: typing.List[str]
    directives: typing.List[str]


CheckerRunFunction = typing.Callable[..., YieldedLintError]
"""Function to run checks.

Returned by ``CodeBlockChecker.create_checker``.
"""
