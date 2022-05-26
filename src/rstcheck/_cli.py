"""CLI for rstcheck."""
import logging
import pathlib
import typing as t

import typer

from rstcheck import _compat as _t, _extras, config as config_mod, runner


ValidReportLevels = _t.Literal["INFO", "WARNING", "ERROR", "SEVERE", "NONE"]

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
    :raises ValueError: On invalid logging leveles.
    """
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {loglevel}")

    logging.basicConfig(level=numeric_level)


def cli(  # pylint: disable=too-many-arguments
    files: t.List[pathlib.Path] = typer.Argument(  # noqa: M511,B008
        ..., allow_dash=True, hidden=True
    ),
    config: t.Optional[pathlib.Path] = typer.Option(  # noqa: M511,B008
        None, "--config", help=HELP_CONFIG
    ),
    warn_unknown_settings: t.Optional[bool] = typer.Option(  # noqa: M511,B008
        None, "--warn-unknown-settings", help=HELP_WARN_UNKNOWN_SETTINGS
    ),
    recursive: t.Optional[bool] = typer.Option(  # noqa: M511,B008
        None, "--recursive", "-r", help=HELP_RECURSIVE
    ),
    report_level: t.Optional[str] = typer.Option(  # noqa: M511,B008
        None, metavar="LEVEL", help=HELP_REPORT_LEVEL
    ),
    log_level: str = typer.Option(  # noqa: M511,B008
        "WARNING", metavar="LEVEL", help=HELP_LOG_LEVEL
    ),
    ignore_directives: t.Optional[str] = typer.Option(  # noqa: M511,B008
        None, help=HELP_IGNORE_DIRECTIVES
    ),
    ignore_roles: t.Optional[str] = typer.Option(None, help=HELP_IGNORE_ROLES),  # noqa: M511,B008
    ignore_substitutions: t.Optional[str] = typer.Option(  # noqa: M511,B008
        None, help=HELP_IGNORE_SUBSTITUTIONS
    ),
    ignore_languages: t.Optional[str] = typer.Option(  # noqa: M511,B008
        None, help=HELP_IGNORE_LANGUAGES
    ),
    ignore_messages: t.Optional[str] = typer.Option(  # noqa: M511,B008
        None, metavar="REGEX", help=HELP_IGNORE_MESSAGES
    ),
) -> int:
    """CLI of rstcheck."""
    setup_logger(log_level)
    logger = logging.getLogger(__name__)

    if pathlib.Path("-") in files and len(files) > 1:
        typer.echo("'-' is only allowed without additional files.", err=True)
        raise typer.Abort()

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

    logger.debug("Create main runner instance.")
    _runner = runner.RstcheckMainRunner(
        check_paths=files, rstcheck_config=rstcheck_config, overwrite_config=False
    )

    logger.info("Run main runner instance.")
    _runner.check()
    exit_code = _runner.print_result()
    raise typer.Exit(code=exit_code)


enabled_features = []
if _extras.SPHINX_INSTALLED:
    enabled_features.append("Sphinx")
if _extras.TOMLI_INSTALLED:  # pragma: no cover
    enabled_features.append("Toml")

cli.__doc__ = f"""CLI of rstcheck.

Enabled features: {enabled_features}

Pass one ore more rst FILES to check.
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
