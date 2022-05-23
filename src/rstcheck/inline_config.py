"""Inline config comment functionality."""
import functools
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


RSTCHECK_CONFIG_COMMENT_REGEX = re.compile(r"\.\. rstcheck: (.*)=(.*)$")
VALID_INLINE_CONFIG_KEYS = ("ignore-languages",)


@functools.lru_cache()
def get_inline_config_from_source(
    source: str, source_origin: types.SourceFileOrString, warn_unknown_settings: bool = False
) -> t.List[types.InlineConfig]:
    """Get rstcheck inline configs from source.

    Unknown configs are ignored.

    :param source: Source to get config from
    :param source_origin: Origin of the source with the inline ignore comments
    :param warn_unknown_settings: If a warning should be logged on unknown settings;
        defaults to :py:obj:`False`
    :return: A list of inline configs
    """
    configs: t.List[types.InlineConfig] = []
    for (idx, line) in enumerate(source.splitlines()):
        match = RSTCHECK_CONFIG_COMMENT_REGEX.search(line)
        if match is None:
            continue

        key = match.group(1).strip()
        value = match.group(2).strip()

        if key not in VALID_INLINE_CONFIG_KEYS:
            if warn_unknown_settings:
                logger.warning(
                    f"Unknown inline config '{key}' found. "
                    f"Source: '{source_origin}' at line {idx + 1}"
                )
            continue

        configs.append(types.InlineConfig(key=key, value=value))

    return configs


def find_ignored_languages(
    source: str, source_origin: types.SourceFileOrString, warn_unknown_settings: bool = False
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
    inline_configs = get_inline_config_from_source(source, source_origin, warn_unknown_settings)
    for inline_config in inline_configs:
        if inline_config["key"] == "ignore-languages":
            for language in inline_config["value"].split(","):
                yield language.strip()
