"""Inline config comment functionality."""
import logging
import re
import typing as t

from . import types


logger = logging.getLogger(__name__)


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
    ... '''))
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
