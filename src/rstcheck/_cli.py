"""CLI for rstcheck."""

from __future__ import annotations

import logging
import pathlib
import typing as t
from importlib.metadata import version

import typer
from rstcheck_core import _extras, config as config_mod, runner

HELP_CONFIG = """Config file to load. Can be a INI file or directory.
If a directory is passed it will be searched for .rstcheck.cfg | setup.cfg.
If 'NONE' is passed no config file is loaded at all.
"""
if _extras.TOMLI_INSTALLED:  # pragma: no cover
    HELP_CONFIG = """Config file to load. Can be a INI or TOML file or directory.
If a directory is passed it will be searched for .rstcheck.cfg | pyproject.toml | setup.cfg.
If 'NONE' is passed no config file is loaded at all.
"""
HELP_WARN_UNKNOWN_SETTINGS = """Log a WARNING for unknown settings in config files.
Can be hidden via --log-level."""
HELP_RECURSIVE = "Recursively search passed directories for RST files to check."
HELP_REPORT_LEVEL = f"""The report level of the linting issues found.
Valid levels are: INFO | WARNING | ERROR | SEVERE | NONE.
Defaults to {config_mod.DEFAULT_REPORT_LEVEL.name}.
Can be set in config file.
"""
HELP_LOG_LEVEL = """The log level of the application for information that is not a linting issue.
Valid levels are: DEBUG | INFO | WARNING | ERROR | CRITICAL.
Defaults to WARNING.
"""
HELP_IGNORE_DIRECTIVES = """Comma-separated-list of directives to add to the ignore list.
Can be set in config file.
"""
HELP_IGNORE_ROLES = """Comma-separated-list of roles to add to the ignore list.
Can be set in config file.
"""
HELP_IGNORE_SUBSTITUTIONS = """Comma-separated-list of substitutions to add to the ignore list.
Can be set in config file.
"""
HELP_IGNORE_LANGUAGES = """Comma-separated-list of languages for code-blocks to add to the ignore
list. The code in ignored code-blocks will not be checked for errors.
Can be set in config file.
"""
HELP_IGNORE_MESSAGES = """A regular expression to match linting issue messages against to ignore.
Can be set in config file.
"""


def setup_logger(loglevel: str) -> None:
    """Set up logging.

    :param loglevel: Level to log at.
    :raises TypeError: On invalid logging leveles.
    """
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        msg = f"Invalid log level: {loglevel}"
        raise TypeError(msg)

    logging.basicConfig(level=numeric_level)


def version_callback(value: bool) -> None:  # noqa: FBT001
    """Print the version and exit."""
    if value:
        typer.echo(f"rstcheck CLI Version: {version('rstcheck')}")
        typer.echo(f"rstcheck-core Version: {version('rstcheck-core')}")
        raise typer.Exit


def cli(  # noqa: PLR0913
    files: t.List[pathlib.Path] = typer.Argument(..., allow_dash=True, hidden=True),  # noqa: UP006
    config: t.Optional[pathlib.Path] = typer.Option(  # noqa: UP007
        None, "--config", help=HELP_CONFIG
    ),
    warn_unknown_settings: t.Optional[bool] = typer.Option(  # noqa: UP007
        None, "--warn-unknown-settings", help=HELP_WARN_UNKNOWN_SETTINGS
    ),
    recursive: t.Optional[bool] = typer.Option(  # noqa: UP007
        None, "--recursive", "-r", help=HELP_RECURSIVE
    ),
    report_level: t.Optional[str] = typer.Option(  # noqa: UP007
        None, metavar="LEVEL", help=HELP_REPORT_LEVEL
    ),
    # TODO:#i# use `t.Literal["INFO", "WARNING", "ERROR", "SEVERE", "NONE"]` when supported
    log_level: str = typer.Option("WARNING", metavar="LEVEL", help=HELP_LOG_LEVEL),
    ignore_directives: t.Optional[str] = typer.Option(  # noqa: UP007
        None, help=HELP_IGNORE_DIRECTIVES
    ),
    ignore_roles: t.Optional[str] = typer.Option(None, help=HELP_IGNORE_ROLES),  # noqa: UP007
    ignore_substitutions: t.Optional[str] = typer.Option(  # noqa: UP007
        None, help=HELP_IGNORE_SUBSTITUTIONS
    ),
    ignore_languages: t.Optional[str] = typer.Option(  # noqa: UP007
        None, help=HELP_IGNORE_LANGUAGES
    ),
    ignore_messages: t.Optional[str] = typer.Option(  # noqa: UP007
        None, metavar="REGEX", help=HELP_IGNORE_MESSAGES
    ),
    version: t.Optional[bool] = typer.Option(  # noqa: ARG001, UP007
        None, "--version", callback=version_callback, is_eager=True
    ),
) -> int:
    """CLI of rstcheck."""
    setup_logger(log_level)
    logger = logging.getLogger(__name__)

    if pathlib.Path("-") in files and len(files) > 1:
        typer.echo("'-' is only allowed without additional files.", err=True)
        raise typer.Abort

    logger.info("Create main configuration from CLI options.")
    rstcheck_config = config_mod.RstcheckConfig(
        config_path=config,
        warn_unknown_settings=warn_unknown_settings,
        recursive=recursive,
        report_level=report_level,
        ignore_directives=ignore_directives,
        ignore_roles=ignore_roles,
        ignore_substitutions=ignore_substitutions,
        ignore_languages=ignore_languages,
        ignore_messages=ignore_messages,
    )

    exit_code = 1

    try:
        logger.debug("Create main runner instance.")
        _runner = runner.RstcheckMainRunner(
            check_paths=files, rstcheck_config=rstcheck_config, overwrite_config=False
        )
        logger.info("Run main runner instance.")
        _runner.check()
        exit_code = _runner.print_result()

    except FileNotFoundError as exc:
        if not exc.strerror == "Passed config path not found.":  # pragma: no cover
            raise
        logger.critical("### Passed config path was not found: '%(path)s'", {"path": exc.filename})

    raise typer.Exit(code=exit_code)


enabled_features = []
if _extras.SPHINX_INSTALLED:
    enabled_features.append("Sphinx")
if _extras.TOMLI_INSTALLED:  # pragma: no cover
    enabled_features.append("Toml")

cli.__doc__ = f"""CLI of rstcheck.

Enabled features: {enabled_features}

Pass one or more RST FILES to check.
Can be files or directories if --recursive is passed too.
Pass "-" if you want to read from stdin.
"""


app = typer.Typer()
app.command()(cli)
typer_click_object = typer.main.get_command(app)


def main() -> None:  # pragma: no cover
    """Run CLI."""
    typer.run(cli)


if __name__ == "__main__":
    main()
