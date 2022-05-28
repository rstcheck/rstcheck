"""Checking functionality."""
import contextlib
import copy
import doctest
import io
import json
import locale
import logging
import os
import pathlib
import re
import shlex
import subprocess  # noqa: S404
import sys
import tempfile
import typing as t
import warnings
import xml.etree.ElementTree  # noqa: S405

import docutils.core
import docutils.io
import docutils.nodes
import docutils.utils

from . import _docutils, _extras, _sphinx, config, inline_config, types


if _extras.SPHINX_INSTALLED:
    import sphinx.application
    import sphinx.environment
    import sphinx.io
    import sphinx.parsers


logger = logging.getLogger(__name__)


EXCEPTION_LINE_NO_REGEX = re.compile(r": line\s+([0-9]+)[^:]*$")
DOCTEST_LINE_NO_REGEX = re.compile(r"line ([0-9]+)")
MARKDOWN_LINK_REGEX = re.compile(r"\[[^\]]+\]\([^\)]+\)")


def check_file(
    source_file: pathlib.Path,
    rstcheck_config: config.RstcheckConfig,
    overwrite_with_file_config: bool = True,
) -> t.List[types.LintError]:
    """Check the given file for issues.

    On every call docutils' caches for roles and directives are cleared by reloading their modules.

    :param source_file: Path to file to check
    :param rstcheck_config: Main configuration of the application
    :param overwrite_with_file_config: If the loaded file config should overwrite the
        ``rstcheck_config``;
        defaults to :py:obj:`True`
    :return: A list of found issues
    """
    logger.info(f"Check file'{source_file}'")
    run_config = _load_run_config(source_file.parent, rstcheck_config, overwrite_with_file_config)
    ignore_dict = _create_ignore_dict_from_config(run_config)

    source = _get_source(source_file)

    _docutils.clean_docutils_directives_and_roles_cache()

    with _sphinx.load_sphinx_if_available():

        all_errors = []
        for error in check_source(
            source,
            source_file=source_file,
            ignores=ignore_dict,
            report_level=run_config.report_level or config.DEFAULT_REPORT_LEVEL,
            warn_unknown_settings=run_config.warn_unknown_settings or False,
        ):
            all_errors.append(error)

    return all_errors


def _load_run_config(
    source_file_dir: pathlib.Path,
    rstcheck_config: config.RstcheckConfig,
    overwrite_config: bool = True,
) -> config.RstcheckConfig:
    """Load file specific config file and create run config.

    If the ``rstcheck_config`` does not contain a ``config_path`` the ``source_file_dir`` directory
    tree is searched for a config file to load and merge into the ``rstcheck_config``. The merge
    strategy is set via ``overwrite_config``.

    :param source_file_dir: Directory of the current file to check
    :param rstcheck_config: Main configuration of the application
    :param overwrite_config: If the loaded config should overwrite the ``rstcheck_config``;
        defaults to :py:obj:`True`
    :return: Merged config
    """
    if rstcheck_config.config_path is not None:
        return rstcheck_config

    file_config = config.load_config_file_from_dir_tree(source_file_dir)

    if file_config is None:
        return rstcheck_config

    run_config = config.merge_configs(
        copy.copy(rstcheck_config), file_config, config_add_is_dominant=overwrite_config
    )
    return run_config


def _get_source(source_file: pathlib.Path) -> str:
    """Get source from file or stdin.

    If the file name is "-" then stdin is read for input instead of a file.

    :param source_file: File path to read contents from
    :return: Loaded content
    """
    if source_file.name == "-":
        logger.info("Load source from stdin.")
        return sys.stdin.read()

    resolved_file_path = source_file.resolve()
    with contextlib.closing(docutils.io.FileInput(source_path=resolved_file_path)) as input_file:
        return t.cast(str, input_file.read())


def _replace_ignored_substitutions(source: str, ignore_substitutions: t.List[str]) -> str:
    """Replace rst substitutions from the ignore list with a dummy.

    :param source: Source to replace substitutions in
    :param ignore_substitutions: Substitutions to replace with dummy
    :return: Cleaned source
    """
    for substitution in ignore_substitutions:
        source = source.replace(f"|{substitution}|", f"x{substitution}x")
    return source


def _create_ignore_dict_from_config(rstcheck_config: config.RstcheckConfig) -> types.IgnoreDict:
    """Extract ignore settings from config and create a :py:class:`rstcheck.types.IgnoreDict`.

    :param rstcheck_config: Config to extract ignore settings from
    :return: :py:class:`rstcheck.types.IgnoreDict`
    """
    return types.IgnoreDict(
        messages=rstcheck_config.ignore_messages,
        languages=rstcheck_config.ignore_languages or [],
        directives=rstcheck_config.ignore_directives or [],
        roles=rstcheck_config.ignore_roles or [],
        substitutions=rstcheck_config.ignore_substitutions or [],
    )


def check_source(  # pylint: disable=too-many-arguments
    source: str,
    source_file: t.Optional[pathlib.Path] = None,
    ignores: t.Optional[types.IgnoreDict] = None,
    report_level: config.ReportLevel = config.DEFAULT_REPORT_LEVEL,
    warn_unknown_settings: bool = False,
) -> types.YieldedLintError:
    """Check the given rst source for issues.

    :param source_file: Path to file the source comes from if it comes from a file;
        defaults to :py:obj:`None`
    :param ignores: Ignore information; defaults to :py:obj:`None`
    :param report_level: Report level; defaults to :py:data:`rstcheck.config.DEFAULT_REPORT_LEVEL`
    :param warn_unknown_settings: If a warning should be logged for unknown settings in config file;
        defaults to :py:obj:`False`
    :param sphinx_app: A :py:class:`sphinx.application.Sphinx` instance to use ofr parsing;
        defaults to :py:obj:`None`
    :return: :py:obj:`None`
    :yield: Found issues
    """
    source_origin: types.SourceFileOrString = source_file or "<string>"
    logger.info(f"Check source from '{source_origin}'")
    ignores = ignores or types.IgnoreDict(
        messages=None, languages=[], directives=[], roles=[], substitutions=[]
    )
    ignores["directives"].extend(
        inline_config.find_ignored_directives(source, source_origin, warn_unknown_settings)
    )
    ignores["roles"].extend(
        inline_config.find_ignored_roles(source, source_origin, warn_unknown_settings)
    )
    ignores["substitutions"].extend(
        inline_config.find_ignored_substitutions(source, source_origin, warn_unknown_settings)
    )
    ignores["languages"].extend(
        inline_config.find_ignored_languages(source, source_origin, warn_unknown_settings)
    )

    source = _replace_ignored_substitutions(source, ignores["substitutions"])

    if not _extras.SPHINX_INSTALLED:
        _docutils.register_rstcheck_code_directives(
            ignore_code_directive="code" in ignores["directives"],
            ignore_codeblock_directive="code-block" in ignores["directives"],
            ignore_sourcecode_directive="sourcecode" in ignores["directives"],
        )

    _docutils.ignore_directives_and_roles(ignores["directives"] or [], ignores["roles"] or [])

    if _extras.SPHINX_INSTALLED:
        _sphinx.load_sphinx_ignores()

    writer = _CheckWriter(source, source_origin, ignores, report_level)

    string_io = io.StringIO()

    # This is a hack to avoid false positive from docutils (#23). docutils mistakes BOMs for actual
    # visible letters. This results in the "underline too short" warning firing.
    # This is tested in the CLI integration tests with the `testing/examples/good/bom.rst` file.
    with contextlib.suppress(UnicodeError):
        source = source.encode("utf-8").decode("utf-8-sig")

    reader = None
    parser = None
    settings_overrides = {
        "halt_level": 5,
        "report_level": report_level.value,
        "warning_stream": string_io,
    }
    source_path = source_origin

    if sphinx_app is not None:
        sphinx_app.env = t.cast(sphinx.environment.BuildEnvironment, sphinx_app.env)

        reader = sphinx.io.SphinxStandaloneReader()
        reader.setup(sphinx_app)

        parser = sphinx.parsers.RSTParser()
        parser.set_application(sphinx_app)

        settings_overrides = {**sphinx_app.env.settings, **settings_overrides}
        source_path = pathlib.Path(source_path).resolve()

        sphinx_app.env.srcdir = str(source_path.parent)
        sphinx_app.env.temp_data["docname"] = str(source_path)

    with contextlib.suppress(docutils.utils.SystemMessage):
        docutils.core.publish_string(
            source,
            reader=reader,
            parser=parser,
            writer=writer,
            source_path=str(source_path),
            settings_overrides=settings_overrides,
        )

    yield from _run_code_checker_and_filter_errors(writer.checkers, ignores["messages"])

    rst_errors = string_io.getvalue().strip()

    if not rst_errors:
        return

    yield from _parse_and_filter_rst_errors(rst_errors, source_origin, ignores["messages"])


def _run_code_checker_and_filter_errors(
    checker_list: t.List[types.CheckerRunFunction],
    # NOTE: Pattern type-arg errors pydanic: https://github.com/samuelcolvin/pydantic/issues/2636
    ignore_messages: t.Optional[t.Pattern] = None,  # type: ignore[type-arg]
) -> types.YieldedLintError:
    """Run each code block checker function and yield filtered :py:class:`rstcheck.types.LintError`.

    :param checker_list: List of code block checker functions
    :param ignore_messages: Regex for ignoring error messages;
        defaults to :py:obj:`None`
    :return: :py:obj:`None`
    :yield: Filtered :py:class:`rstcheck.types.LintError` s from run checker function
    """
    for checker in checker_list:
        for lint_error in checker():
            if ignore_messages and ignore_messages.search(lint_error["message"]):
                continue
            yield lint_error


def _parse_and_filter_rst_errors(
    rst_errors: str,
    # NOTE: Pattern type-arg errors pydanic: https://github.com/samuelcolvin/pydantic/issues/2636
    source_origin: types.SourceFileOrString,
    ignore_messages: t.Optional[t.Pattern] = None,  # type: ignore[type-arg]
) -> types.YieldedLintError:
    """Parse rst errors and yield filtered :py:class:`rstcheck.types.LintError`.

    :param rst_errors: String with rst errors
    :param source_origin: Origin of the source with the errors
    :param ignore_messages: Regex for ignoring error messages;
        defaults to :py:obj:`None`
    :return: :py:obj:`None`
    :yield: Parsed and filtered :py:class:`rstcheck.types.LintError` s
    """
    for message in rst_errors.splitlines():
        with contextlib.suppress(ValueError):
            if ignore_messages and ignore_messages.search(message):
                continue
            yield _parse_gcc_style_error_message(
                message, source_origin=source_origin, has_column=False
            )


class _CheckWriter(docutils.writers.Writer):
    """Runs CheckTranslator on code blocks."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        source: str,
        source_origin: types.SourceFileOrString,
        ignores: t.Optional[types.IgnoreDict] = None,
        report_level: config.ReportLevel = config.DEFAULT_REPORT_LEVEL,
        warn_unknown_settings: bool = False,
    ) -> None:
        """Inititalize :py:class:`_CheckWriter`.

        :param source: Rst source to check
        :param source_origin: Path to file the source comes from
        :param ignores: Ignore information; defaults to :py:obj:`None`
        :param report_level: Report level;
            defaults to :py:data:`rstcheck.config.DEFAULT_REPORT_LEVEL`
        :param warn_unknown_settings: If a warning should be logged for unknown settings in config
            file;
            defaults to :py:obj:`False`
        """
        docutils.writers.Writer.__init__(self)
        self.checkers: t.List[types.CheckerRunFunction] = []
        self.source = source
        self.source_origin = source_origin
        self.ignores = ignores
        self.report_level = report_level
        self.warn_unknown_settings = warn_unknown_settings

    def translate(self) -> None:
        """Run CheckTranslator."""
        visitor = _CheckTranslator(
            self.document,
            source=self.source,
            source_origin=self.source_origin,
            ignores=self.ignores,
            report_level=self.report_level,
            warn_unknown_settings=self.warn_unknown_settings,
        )
        self.document.walkabout(visitor)
        self.checkers += visitor.checkers


class _CheckTranslator(docutils.nodes.NodeVisitor):  # pylint: disable=too-many-instance-attributes
    """Visits code blocks and checks for syntax errors in code."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        document: docutils.nodes.document,
        source: str,
        source_origin: types.SourceFileOrString,
        ignores: t.Optional[types.IgnoreDict] = None,
        report_level: config.ReportLevel = config.DEFAULT_REPORT_LEVEL,
        warn_unknown_settings: bool = False,
    ) -> None:
        """Inititalize :py:class:`_CheckTranslator`.

        :param document: Document node
        :param source: Rst source to check
        :param source_origin: Path to file the source comes from
        :param ignores: Ignore information; defaults to :py:obj:`None`
        :param report_level: Report level;
            defaults to :py:data:`rstcheck.config.DEFAULT_REPORT_LEVEL`
        :param warn_unknown_settings: If a warning should be logged for unknown settings in config
            file;
            defaults to :py:obj:`False`
        """
        docutils.nodes.NodeVisitor.__init__(self, document)
        self.checkers: t.List[types.CheckerRunFunction] = []
        self.source = source
        self.source_origin = source_origin
        self.ignores = ignores or types.IgnoreDict(
            messages=None, languages=[], directives=[], roles=[], substitutions=[]
        )
        self.report_level = report_level
        self.warn_unknown_settings = warn_unknown_settings
        self.code_block_checker = CodeBlockChecker(
            source_origin, ignores, report_level, warn_unknown_settings
        )
        self.code_block_ignore_lines = list(
            inline_config.find_code_block_ignore_lines(
                source=self.source,
                source_origin=self.source_origin,
                warn_unknown_settings=self.warn_unknown_settings,
            )
        )

    def visit_doctest_block(self, node: docutils.nodes.Element) -> None:
        """Add check for syntax of doctest.

        :param node: The doctest node
        """
        if "doctest" in self.ignores["languages"]:
            return

        self._add_check(
            node=node,
            run=self.code_block_checker.create_checker(node.rawsource, "doctest"),
            language="doctest",
            is_code_node=False,
        )

    def visit_literal_block(self, node: docutils.nodes.Element) -> None:
        """Add check for syntax of code block.

        :param node: The code block node
        :raises docutils.nodes.SkipNode: After a check was added or nothing to do
        """
        # For "..code-block:: language"
        language = node.get("language", None)
        is_code_node = False
        if not language:
            # For "..code:: language"
            is_code_node = True
            classes = node.get("classes")
            if "code" not in classes:
                return
            language = classes[-1]

        directive_line = _get_code_block_directive_line(node, self.source)
        if directive_line is None:
            logger.error(
                "Could not find line for literal block directive. "
                f"Source: '{self.source_origin}' at line {node.line}"
            )
            return

        if directive_line - 1 in self.code_block_ignore_lines:
            logger.debug(
                "Skipping code-block due to skip comment. "
                f"Source: '{self.source_origin}' at line {node.line}"
            )
            return

        if language in self.ignores["languages"]:
            return

        if language == "doctest" or (
            language == "python" and node.rawsource.lstrip().startswith(">>> ")
        ):
            self.visit_doctest_block(node)
            raise docutils.nodes.SkipNode

        if self.code_block_checker.language_is_supported(language):
            run = self.code_block_checker.create_checker(node.rawsource, language)
            self._add_check(node=node, run=run, language=language, is_code_node=is_code_node)

        raise docutils.nodes.SkipNode

    def visit_paragraph(self, node: docutils.nodes.Element) -> None:
        """Check syntax of reStructuredText.

        :param node: The rst node
        """
        find = MARKDOWN_LINK_REGEX.search(node.rawsource)
        if find is not None:
            self.document.reporter.warning(
                "(rst) Link is formatted in Markdown style.", base_node=node
            )

    def _add_check(  # noqa: CCR001
        self,
        node: docutils.nodes.Element,
        run: types.CheckerRunFunction,
        language: str,
        is_code_node: bool,
    ) -> None:
        """Add node checker that will be run.

        :param node: The node to check
        :param run: The runner function that checks the node
        :param language: The language of the node
        :param is_code_node: If it is a code block node
        """

        def run_check() -> types.YieldedLintError:  # noqa: CCR001
            """Yield found issues."""
            all_results = run()
            if all_results is not None:
                if all_results:
                    for result in all_results:
                        error_offset = result["line_number"] - 1

                        line_number = getattr(node, "line", None)
                        if line_number is not None:
                            yield types.LintError(
                                source_origin=result["source_origin"],
                                line_number=_beginning_of_code_block(
                                    node=node,
                                    line_number=line_number,
                                    full_contents=self.source,
                                    is_code_node=is_code_node,
                                )
                                + error_offset,
                                message=f"({language}) {result['message']}",
                            )
                else:
                    yield types.LintError(
                        source_origin=self.source_origin, line_number=0, message="unknown error"
                    )

        self.checkers.append(run_check)

    def unknown_visit(self, node: docutils.nodes.Node) -> None:
        """Ignore."""

    def unknown_departure(self, node: docutils.nodes.Node) -> None:
        """Ignore."""


def _beginning_of_code_block(
    node: docutils.nodes.Element, line_number: int, full_contents: str, is_code_node: bool
) -> int:
    """Get line number of beginning of code block.

    :param node: The code block node
    :param line_number: The current line number
    :param full_contents: The node's contents
    :param is_code_node: If it is a code block node
    :return: First fine number of the block
    """
    if _extras.SPHINX_INSTALLED and not is_code_node:
        sphinx_code_block_delta = -1
        delta = len(node.non_default_attributes())
        current_line_contents = full_contents.splitlines()[line_number:]
        blank_lines = next((i for (i, x) in enumerate(current_line_contents) if x), 0)
        return line_number + delta - 1 + blank_lines - 1 + sphinx_code_block_delta

    lines = full_contents.splitlines()
    code_block_length = len(node.rawsource.splitlines())

    with contextlib.suppress(IndexError):
        # Case where there are no extra spaces.
        if lines[line_number - 1].strip():
            return line_number - code_block_length + 1

    # The offsets are wrong if the RST text has multiple blank lines after
    # the code block. This is a workaround.
    for line_no in range(line_number, 1, -1):
        if lines[line_no - 2].strip():
            break

    return line_no - code_block_length


CODE_BLOCK_RE = re.compile(r"\.\. code::|\.\. code-block::|\.\. sourcecode::")


def _get_code_block_directive_line(
    node: docutils.nodes.Element, full_contents: str
) -> t.Optional[int]:
    """Find line of code block directive.

    :param node: The code block node
    :param full_contents: The node's contents
    :return: Line of code block directive or :py:obj:`None`
    """
    line_number = node.line
    if line_number is None:
        return None

    if _extras.SPHINX_INSTALLED:
        return line_number

    lines = full_contents.splitlines()
    for line_no in range(line_number, 1, -1):
        if CODE_BLOCK_RE.match(lines[line_no - 2].strip()) is not None:
            return line_no - 1

    return None


class CodeBlockChecker:
    """Checker for code blockes with different languages."""

    def __init__(
        self,
        source_origin: types.SourceFileOrString,
        ignores: t.Optional[types.IgnoreDict] = None,
        report_level: config.ReportLevel = config.DEFAULT_REPORT_LEVEL,
        warn_unknown_settings: bool = False,
    ) -> None:
        """Inititalize CodeBlockChecker.

        :param source_origin: Path to file the source comes from
        :param ignores: Ignore information; defaults to :py:obj:`None`
        :param report_level: Report level;
            defaults to :py:data:`rstcheck.config.DEFAULT_REPORT_LEVEL`
        :param warn_unknown_settings: If a warning should be logged for unknown settings in config
            file;
            defaults to :py:obj:`False`
        """
        self.source_origin = source_origin
        self.ignores = ignores
        self.report_level = report_level
        self.warn_unknown_settings = warn_unknown_settings

    def language_is_supported(self, language: str) -> bool:
        """Check if given language can be checked.

        :param language: Language to check
        :return: If langauge can be checked
        """
        return getattr(self, f"check_{language}", None) is not None

    def create_checker(self, source_code: str, language: str) -> types.CheckerRunFunction:
        """Create a checker function for the given source and language.

        :param source: Source code to check
        :param language: Language of the source code
        :return: Checker function
        """
        return lambda: self.check(source_code, language)

    def check(self, source_code: str, language: str) -> types.YieldedLintError:
        """Call the appropiate checker function for the given langauge to check given source.

        :param source: Source code to check
        :param language: Language of the source code
        :return: :py:obj:`None` if language is not supported
        :yield: Found issues
        """
        checker_function = t.Callable[[str], types.YieldedLintError]
        checker: t.Optional[checker_function] = getattr(self, f"check_{language}", None)
        if checker is None:
            return None

        yield from checker(source_code)
        return None

    def check_python(self, source_code: str) -> types.YieldedLintError:
        """Check python source for syntax errors.

        :param source: Python source code to check
        :return: :py:obj:`None`
        :yield: Found issues
        """
        logger.debug("Check python source.")
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", SyntaxWarning)
                compile(source_code, "<string>", "exec")
        except SyntaxError as exception:
            yield types.LintError(
                source_origin=self.source_origin,
                line_number=int(exception.lineno or 0),
                message=exception.msg,
            )

    def check_json(self, source_code: str) -> types.YieldedLintError:
        """Check JSON source for syntax errors.

        :param source: JSON source code to check
        :return: :py:obj:`None`
        :yield: Found issues
        """
        logger.debug("Check JSON source.")
        try:
            json.loads(source_code)
        except ValueError as exception:
            message = f"{exception}"
            found = EXCEPTION_LINE_NO_REGEX.search(message)
            line_number = int(found.group(1)) if found else 0

            yield types.LintError(
                source_origin=self.source_origin, line_number=int(line_number), message=message
            )

    def check_xml(self, source_code: str) -> types.YieldedLintError:
        """Check XML source for syntax errors.

        :param source: XML source code to check
        :return: :py:obj:`None`
        :yield: Found issues
        """
        logger.debug("Check XML source.")
        try:
            xml.etree.ElementTree.fromstring(source_code)  # noqa: S314
        except xml.etree.ElementTree.ParseError as exception:
            message = f"{exception}"
            found = EXCEPTION_LINE_NO_REGEX.search(message)
            line_number = int(found.group(1)) if found else 0

            yield types.LintError(
                source_origin=self.source_origin, line_number=int(line_number), message=message
            )

    def check_rst(self, source_code: str) -> types.YieldedLintError:
        """Check nested rst source for syntax errors.

        :param source: rst source code to check
        :return: :py:obj:`None`
        :yield: Found issues
        """
        logger.debug("Check RST source.")
        yield from check_source(
            source_code,
            source_file=None,
            ignores=self.ignores,
            report_level=self.report_level,
            warn_unknown_settings=self.warn_unknown_settings,
        )

    def check_doctest(self, source_code: str) -> types.YieldedLintError:
        """Check doctest source for syntax errors.

        This does not run the test as that would be unsafe. Nor does this
        check the Python syntax in the doctest. That could be purposely
        incorrect for testing purposes.

        :param source: XML source code to check
        :return: :py:obj:`None`
        :yield: Found issues
        """
        logger.debug("Check doctest source.")
        parser = doctest.DocTestParser()
        try:
            parser.parse(source_code)
        except ValueError as exception:
            message = f"{exception}"
            match = DOCTEST_LINE_NO_REGEX.match(message)
            if match:
                yield types.LintError(
                    source_origin=self.source_origin,
                    line_number=int(match.group(1)),
                    message=message,
                )

    def check_bash(self, source_code: str) -> types.YieldedLintError:
        """Check bash source for syntax errors.

        :param source: bash source code to check
        :return: :py:obj:`None`
        :yield: Found issues
        """
        logger.debug("Check bash source.")
        result = self._run_in_subprocess(source_code, ".bash", ["bash", "-n"])

        if result:
            (output, filename) = result
            prefix = str(filename) + ": line "
            for line in output.splitlines():
                if not line.startswith(prefix):  # pragma: no cover # NOTE: Case not reproducible
                    continue
                message = line[len(prefix) :]
                split_message = message.split(":", 1)
                yield types.LintError(
                    source_origin=self.source_origin,
                    line_number=int(split_message[0]) - 1,
                    message=split_message[1].strip(),
                )

    def check_c(self, source_code: str) -> types.YieldedLintError:
        """Check C source for syntax errors.

        :param source: C source code to check
        :return: :py:obj:`None`
        :yield: Found issues
        """
        logger.debug("Check C source.")
        return self._gcc_checker(
            source_code,
            ".c",
            [os.getenv("CC", "gcc")]
            + shlex.split(os.getenv("CFLAGS", ""))
            + shlex.split(os.getenv("CPPFLAGS", ""))
            + ["-I.", "-I.."],
        )

    def check_cpp(self, source_code: str) -> types.YieldedLintError:
        """Check C++ source for syntax errors.

        :param source: C++ source code to check
        :return: :py:obj:`None`
        :yield: Found issues
        """
        logger.debug("Check C++ source.")
        yield from self._gcc_checker(
            source_code,
            ".cpp",
            [os.getenv("CXX", "g++")]
            + shlex.split(os.getenv("CXXFLAGS", ""))
            + shlex.split(os.getenv("CPPFLAGS", ""))
            + ["-I.", "-I.."],
        )

    def _gcc_checker(
        self, source_code: str, filename_suffix: str, arguments: t.List[str]
    ) -> types.YieldedLintError:
        """Check code blockes using gcc (Helper function).

        :param source_code: Source code to check
        :param filename_suffix: File suffix for language of the source code
        :param arguments: Command and arguments to run
        :return: :py:obj:`None`
        :yield: Found issues
        """
        result = self._run_in_subprocess(
            source_code, filename_suffix, arguments + ["-pedantic", "-fsyntax-only"]
        )

        if result:
            (output, temp_file_name) = result
            for line in output.splitlines():
                try:
                    yield _parse_gcc_style_error_message(line, source_origin=temp_file_name)
                except ValueError:
                    continue

    def _run_in_subprocess(
        self,
        code: str,
        filename_suffix: str,
        arguments: t.List[str],
    ) -> t.Optional[t.Tuple[str, pathlib.Path]]:
        """Run checker in a subprocess (Helper function).

        :param source_code: Source code to check
        :param filename_suffix: File suffix for language of the source code
        :param arguments: Command and arguments to run
        :return: :py:obj:`None` if no issues were found else a tuple of the stderr and temp-file
            name
        """
        get_encoding = lambda: locale.getpreferredencoding() or sys.getdefaultencoding()

        source_origin_path = self.source_origin
        if isinstance(source_origin_path, str):
            source_origin_path = pathlib.Path(source_origin_path)

        # NOTE: On windows a file cannot be opened twice.
        # Therefore close it before using it in subprocess.
        temporary_file = tempfile.NamedTemporaryFile(  # pylint: disable=consider-using-with
            mode="wb", suffix=filename_suffix, delete=False
        )
        temporary_file_path = pathlib.Path(temporary_file.name)
        try:
            temporary_file.write(code.encode("utf-8"))
            temporary_file.flush()
            temporary_file.close()

            result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603
                arguments + [temporary_file.name],
                capture_output=True,
                cwd=source_origin_path.parent,
            )

            if result.returncode != 0:
                return (result.stderr.decode(get_encoding()), temporary_file_path)
            return None
        finally:
            temporary_file_path.unlink()


def _parse_gcc_style_error_message(
    message: str, source_origin: types.SourceFileOrString, has_column: bool = True
) -> types.LintError:
    """Parse GCC-style error message.

    Return (line_number, message). Raise ValueError if message cannot be
    parsed.

    :param message: Message to parse
    :param filename: File the message is associated with
    :param has_column: The the message has a column number; defaults to :py:obj:`True`
    :raises ValueError: If the message cannot be parsed
    :return: Parsed message
    """
    colons = 2 if has_column else 1
    prefix = str(source_origin) + ":"
    if not message.startswith(prefix):
        logger.warning(f"Skipping unparsable message: '{message}'.")
        raise ValueError("Message cannot be parsed.")
    message = message[len(prefix) :]
    split_message = message.split(":", colons)
    line_number = int(split_message[0])
    return types.LintError(
        source_origin=source_origin, line_number=line_number, message=split_message[colons].strip()
    )
