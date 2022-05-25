"""Inline config comment functionality."""
import functools
import logging
import re
import typing as t

from . import _compat as _t, types


logger = logging.getLogger(__name__)


RSTCHECK_CONFIG_COMMENT_REGEX = re.compile(r"\.\. rstcheck: (.*)=(.*)$")
VALID_INLINE_CONFIG_KEYS = (
    "ignore-directives",
    "ignore-roles",
    "ignore-substitutions",
    "ignore-languages",
)
ValidInlineConfigKeys = t.Union[
    _t.Literal["ignore-directives"],
    _t.Literal["ignore-roles"],
    _t.Literal["ignore-substitutions"],
    _t.Literal["ignore-languages"],
]

RSTCHECK_FLOW_CONTROL_COMMENT_REGEX = re.compile(r"\.\. rstcheck: ([a-z-]*)$")
VALID_INLINE_FLOW_CONTROLS = ("ignore-next-code-block",)


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


def _filter_config_and_split_values(
    target_config: ValidInlineConfigKeys,
    source: str,
    source_origin: types.SourceFileOrString,
    warn_unknown_settings: bool = False,
) -> t.Generator[str, None, None]:
    """Get specified configs and comma split them.

    :param target_config: Config target to filter for
    :param source: Source to get config from
    :param source_origin: Origin of the source with the inline ignore comments
    :param warn_unknown_settings: If a warning should be logged on unknown settings;
        defaults to :py:obj:`False`
    :return: None
    :yield: Single values for the ``target_config``
    """
    inline_configs = get_inline_config_from_source(source, source_origin, warn_unknown_settings)
    for inline_config in inline_configs:
        if inline_config["key"] == target_config:
            for language in inline_config["value"].split(","):
                yield language.strip()


def find_ignored_directives(
    source: str, source_origin: types.SourceFileOrString, warn_unknown_settings: bool = False
) -> t.Generator[str, None, None]:
    """Search the rst source for rstcheck inline ignore-directives comments.

    Directives are ignored via comment.

    For example, to ignore directive1, directive2, and directive3:

    .. testsetup::

        from rstcheck.inline_config import find_ignored_directives

    >>> list(find_ignored_directives('''
    ... Example
    ... =======
    ...
    ... .. rstcheck: ignore-directives=directive1,directive3
    ...
    ... .. rstcheck: ignore-directives=directive2
    ... ''', "<string>"))
    ['directive1', 'directive3', 'directive2']

    :param source: Rst source code
    :param source_origin: Origin of the source with the inline ignore comments
    :return: None
    :yield: Found directives to ignore
    """
    yield from _filter_config_and_split_values(
        "ignore-directives", source, source_origin, warn_unknown_settings
    )


def find_ignored_roles(
    source: str, source_origin: types.SourceFileOrString, warn_unknown_settings: bool = False
) -> t.Generator[str, None, None]:
    """Search the rst source for rstcheck inline ignore-roles comments.

    Roles are ignored via comment.

    For example, to ignore role1, role2, and role3:

    .. testsetup::

        from rstcheck.inline_config import find_ignored_roles

    >>> list(find_ignored_roles('''
    ... Example
    ... =======
    ...
    ... .. rstcheck: ignore-roles=role1,role3
    ...
    ... .. rstcheck: ignore-roles=role2
    ... ''', "<string>"))
    ['role1', 'role3', 'role2']

    :param source: Rst source code
    :param source_origin: Origin of the source with the inline ignore comments
    :return: None
    :yield: Found roles to ignore
    """
    yield from _filter_config_and_split_values(
        "ignore-roles", source, source_origin, warn_unknown_settings
    )


def find_ignored_substitutions(
    source: str, source_origin: types.SourceFileOrString, warn_unknown_settings: bool = False
) -> t.Generator[str, None, None]:
    """Search the rst source for rstcheck inline ignore-substitutions comments.

    Substitutions are ignored via comment.

    For example, to ignore substitution1, substitution2, and substitution3:

    .. testsetup::

        from rstcheck.inline_config import find_ignored_substitutions

    >>> list(find_ignored_substitutions('''
    ... Example
    ... =======
    ...
    ... .. rstcheck: ignore-substitutions=substitution1,substitution3
    ...
    ... .. rstcheck: ignore-substitutions=substitution2
    ... ''', "<string>"))
    ['substitution1', 'substitution3', 'substitution2']

    :param source: Rst source code
    :param source_origin: Origin of the source with the inline ignore comments
    :return: None
    :yield: Found substitutions to ignore
    """
    yield from _filter_config_and_split_values(
        "ignore-substitutions", source, source_origin, warn_unknown_settings
    )


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
    yield from _filter_config_and_split_values(
        "ignore-languages", source, source_origin, warn_unknown_settings
    )


@functools.lru_cache()
def get_inline_flow_control_from_source(
    source: str, source_origin: types.SourceFileOrString, warn_unknown_settings: bool = False
) -> t.List[types.InlineFlowControl]:
    """Get rstcheck inline flow control from source.

    Unknown flow controls are ignored.

    :param source: Source to get config from
    :param source_origin: Origin of the source with the inline flow control
    :param warn_unknown_settings: If a warning should be logged on unknown settings;
        defaults to :py:obj:`False`
    :return: A list of inline flow controls
    """
    configs: t.List[types.InlineFlowControl] = []
    for (idx, line) in enumerate(source.splitlines()):
        match = RSTCHECK_FLOW_CONTROL_COMMENT_REGEX.search(line)
        if match is None:
            continue

        value = match.group(1).strip()
        line_number = idx + 1

        if value not in VALID_INLINE_FLOW_CONTROLS:
            if warn_unknown_settings:
                logger.warning(
                    f"Unknown inline flow control '{value}' found. "
                    f"Source: '{source_origin}' at line {line_number}"
                )
            continue

        configs.append(types.InlineFlowControl(value=value, line_number=line_number))

    return configs


def find_code_block_ignore_lines(
    source: str,
    source_origin: types.SourceFileOrString,
    warn_unknown_settings: bool = False,
) -> t.Generator[int, None, None]:
    """Get lines of ``ignore-next-code-block`` flow control comments.

    :param source: Source to get config from
    :param source_origin: Origin of the source with the inline ignore comments
    :param warn_unknown_settings: If a warning should be logged on unknown settings;
        defaults to :py:obj:`False`
    :return: None
    :yield: Single values for the ``target_config``
    """
    flow_controls = get_inline_flow_control_from_source(
        source, source_origin, warn_unknown_settings
    )
    for flow_control in flow_controls:
        if flow_control["value"] == "ignore-next-code-block":
            yield flow_control["line_number"]
