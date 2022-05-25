"""Helper types."""
import pathlib
import typing as t

from . import _compat as _t


SourceFileOrString = t.Union[pathlib.Path, _t.Literal["<string>"]]
"""Path to source file or if it is a string then '<string>'."""


class LintError(_t.TypedDict):
    """Dict with information about an linting error."""

    source_origin: SourceFileOrString
    line_number: int
    message: str


YieldedLintError = t.Generator[LintError, None, None]
"""Yielded version of type :py:class:`LintError`."""


class IgnoreDict(_t.TypedDict):
    """Dict with ignore information."""

    # NOTE: Pattern type-arg errors pydanic: https://github.com/samuelcolvin/pydantic/issues/2636
    messages: t.Optional[t.Pattern]  # type: ignore[type-arg]
    languages: t.List[str]
    directives: t.List[str]
    roles: t.List[str]
    substitutions: t.List[str]


CheckerRunFunction = t.Callable[..., YieldedLintError]
"""Function to run checks.

Returned by :py:meth:`rstcheck.checker.CodeBlockChecker.create_checker`.
"""


class InlineConfig(_t.TypedDict):
    """Dict with a config key and config value comming from a inline config comment."""

    key: str
    value: str


class InlineFlowControl(_t.TypedDict):
    """Dict with a flow control value and line number comming from a inline config comment."""

    value: str
    line_number: int
