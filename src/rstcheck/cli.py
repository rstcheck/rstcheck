"""CLI for rstcheck."""
import pathlib
import typing

import typer

from rstcheck import _compat, _extras, config as config_mod, runner


ValidReportLevels = _compat.Literal["INFO", "WARNING", "ERROR", "SEVERE", "NONE"]

HELP_FILES = "RST files to check. Can be files or directories if --recursive is passed too."
HELP_CONFIG = """Config file to load. Can be a INI file or directory.
If a directory is passed it will be searched for .rstcheck.cfg | setup.cfg.
"""
if _extras.TOMLI_INSTALLED:
    HELP_CONFIG = """Config file to load. Can be a INI or TOML file or directory.
If a directory is passed it will be searched for .rstcheck.cfg | pyproject.toml | setup.cfg.
"""
HELP_RECURSIVE = "Recursively search passed directories for RST files to check."
HELP_REPORT_LEVEL = """The report level of the linting issues found.
Can be set in config file.
Valid levels are: INFO | WARNING | ERROR | SEVERE | NONE.
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


def cli(  # pylint: disable=too-many-arguments
    files: typing.List[pathlib.Path] = typer.Argument(  # noqa: M511,B008
        ..., help=HELP_FILES, allow_dash=True
    ),
    config: typing.Optional[pathlib.Path] = typer.Option(  # noqa: M511,B008
        None, "--config", help=HELP_CONFIG
    ),
    recursive: bool = typer.Option(  # noqa: M511,B008
        False, "--recursive", "-r", help=HELP_RECURSIVE
    ),
    report_level: str = typer.Option(  # noqa: M511,B008
        "INFO", metavar="LEVEL", help=HELP_REPORT_LEVEL
    ),
    ignore_directives: typing.Optional[str] = typer.Option(  # noqa: M511,B008
        None, help=HELP_IGNORE_DIRECTIVES
    ),
    ignore_roles: typing.Optional[str] = typer.Option(  # noqa: M511,B008
        None, help=HELP_IGNORE_ROLES
    ),
    ignore_substitutions: typing.Optional[str] = typer.Option(  # noqa: M511,B008
        None, help=HELP_IGNORE_SUBSTITUTIONS
    ),
    ignore_languages: typing.Optional[str] = typer.Option(  # noqa: M511,B008
        None, help=HELP_IGNORE_LANGUAGES
    ),
    ignore_messages: typing.Optional[str] = typer.Option(  # noqa: M511,B008
        None, metavar="REGEX", help=HELP_IGNORE_MESSAGES
    ),
) -> int:
    """CLI of rstcheck."""
    _config = config_mod.RstcheckConfig(
        check_paths=files,
        config_path=config,
        recursive=recursive,
        report_level=report_level,
        ignore_directives=ignore_directives,
        ignore_roles=ignore_roles,
        ignore_substitutions=ignore_substitutions,
        ignore_languages=ignore_languages,
        ignore_messages=ignore_messages,
    )
    _runner = runner.RstcheckMainRunner(main_config=_config, overwrite_config=False)
    _runner.check()
    exit_code = _runner.get_result()
    raise typer.Exit(code=exit_code)


def main() -> None:
    """Run CLI."""
    typer.run(cli)


if __name__ == "__main__":
    main()
