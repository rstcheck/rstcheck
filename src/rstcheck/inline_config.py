"""Inline config comment functionality."""
import re
import typing


RSTCHECK_COMMENT_REGEX = re.compile(r"\.\. rstcheck:")


class RstcheckCommentSyntaxError(Exception):
    """Syntax error for rstcheck inline config comments."""

    def __init__(self, message: str, line_number: int) -> None:
        """Initialize the ``RstcheckCommentSyntaxError`` exception.

        :param message: Error message
        :param line_number: Line number where the error occured
        """
        self.line_number = line_number
        Exception.__init__(self, message)


def find_ignored_languages(source: str) -> typing.Generator[str, None, None]:  # noqa: CCR001
    """Search the rst source for rstcheck inline ignore-languages comments.

    Languages are ignored via comment.

    For example, to ignore C++, JSON, and Python:

    >>> list(find_ignored_languages('''
    ... Example
    ... =======
    ...
    ... .. rstcheck: ignore-languages=cpp,json
    ...
    ... .. rstcheck: ignore-languages=python
    ... '''))
    ["cpp", "json", "python"]

    :param source: Rst source code
    :raises RstcheckCommentSyntaxError: When the comment has invalid syntax
    :return: None
    :yield: Found languages to ignore
    """
    for (index, line) in enumerate(source.splitlines()):
        match = RSTCHECK_COMMENT_REGEX.match(line)
        if match:
            key_and_value = line[match.end() :].strip().split("=")
            if len(key_and_value) != 2:
                raise RstcheckCommentSyntaxError(
                    'Expected "key=value" syntax', line_number=index + 1
                )

            if key_and_value[0] == "ignore-languages":
                for language in key_and_value[1].split(","):
                    yield language.strip()
