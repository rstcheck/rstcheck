"""Helper types."""
import pathlib
import typing as t

from . import _compat


SourceFileOrString = t.Union[pathlib.Path, _compat.Literal["<string>"]]
"""Path to source file or if it is a string then '<string>'."""


class LintError(_compat.TypedDict):
    """Dict with information about an linting error."""

    source_origin: SourceFileOrString
    line_number: int
    message: str


YieldedLintError = t.Generator[LintError, None, None]
"""Yielded version of type ``LintError``."""


class IgnoreDict(_compat.TypedDict):
    """Dict with ignore information."""

    # NOTE: Pattern type-arg errors pydanic: https://github.com/samuelcolvin/pydantic/issues/2636
    messages: t.Optional[t.Pattern]  # type: ignore[type-arg]
    languages: t.List[str]
    directives: t.List[str]
    substitutions: t.List[str]


CheckerRunFunction = t.Callable[..., YieldedLintError]
"""Function to run checks.

Returned by ``CodeBlockChecker.create_checker``.
"""
