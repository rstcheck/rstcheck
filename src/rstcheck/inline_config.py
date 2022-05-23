"""Inline config comment functionality."""
import logging
import re
import typing as t

import pydantic

from . import config, types


logger = logging.getLogger(__name__)


class RstcheckConfigInline(
    pydantic.BaseModel  # pylint: disable=no-member
):  # pylint: disable=too-few-public-methods
    """Type for inline config in rst source.

    :raises pydantic.error_wrappers.ValidationError: If setting is not parsable into correct type
    """

    ignore_directives: t.Optional[t.List[str]]
    ignore_roles: t.Optional[t.List[str]]
    ignore_substitutions: t.Optional[t.List[str]]
    ignore_languages: t.Optional[t.List[str]]

    @pydantic.validator(
        "ignore_directives", "ignore_roles", "ignore_substitutions", "ignore_languages", pre=True
    )
    @classmethod
    def split_str(cls, value: t.Any) -> t.Optional[t.List[str]]:  # noqa: ANN401
        """Validate and parse the following ignore_* settings.

        - ignore_directives
        - ignore_roles
        - ignore_substitutions
        - ignore_languages

        Comma separated strings are split into a list.

        :param value: Value to validate
        :raises ValueError: If not a :py:class:`str` or :py:class:`list` of :py:class:`str`
        :return: List of things to ignore in the respective category
        """
        return config._split_str_validator(value)  # pylint: disable=protected-access


RSTCHECK_COMMENT_REGEX = re.compile(r"\.\. rstcheck:")


def find_ignored_languages(
    source: str, source_origin: types.SourceFileOrString
) -> t.Generator[str, None, None]:
    """Search the rst source for rstcheck inline ignore-languages comments.

    Languages are ignored via comment.

    For example, to ignore C++, JSON, and Python:

    .. testsetup::

        from rstcheck.inline_config import find_ignored_languages

    >>> list(find_ignored_languages('''
    ... Example
    ... =======
    ...
    ... .. rstcheck: ignore-languages=cpp,json
    ...
    ... .. rstcheck: ignore-languages=python
    ... ''', "<string>"))
    ['cpp', 'json', 'python']

    :param source: Rst source code
    :param source_origin: Origin of the source with the inline ignore comments
    :return: None
    :yield: Found languages to ignore
    """
    for (index, line) in enumerate(source.splitlines()):
        match = RSTCHECK_COMMENT_REGEX.match(line)
        if match is None:
            continue

        key_and_value = line[match.end() :].strip().split("=")
        if len(key_and_value) != 2:
            logger.warning(
                'Skipping invalid inline ignore syntax. Expected "key=value" syntax. '
                f"Source: '{source_origin}' at line {index + 1}"
            )
            continue

        if key_and_value[0].strip() == "ignore-languages":
            for language in key_and_value[1].strip().split(","):
                yield language.strip()
