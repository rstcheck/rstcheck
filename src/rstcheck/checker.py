"""Checking functionality."""
import contextlib
import copy
import doctest
import io
import json
import locale
import os
import pathlib
import re
import shlex
import subprocess  # noqa: S404
import sys
import tempfile
import typing
import xml.etree.ElementTree  # noqa: S405

import docutils.core
import docutils.io
import docutils.nodes
import docutils.utils

from . import _docutils, _extras, _sphinx, config, inline_config, types


EXCEPTION_LINE_NO_REGEX = re.compile(r": line\s+([0-9]+)[^:]*$")
DOCTEST_LINE_NO_REGEX = re.compile(r"line ([0-9]+)")
MARKDOWN_LINK_REGEX = re.compile(r"\[[^\]]+\]\([^\)]+\)")


def check_file(
    source_file: pathlib.Path,
    rstcheck_config: config.RstcheckConfig,
    overwrite_with_file_config: bool = True,
) -> typing.List[types.LintError]:
    """Check the given file for issues.

    :param source_file: Path to file to check
    :param rstcheck_config: Main configuration of the application
    :param overwrite_with_file_config: If the loaded file config should overwrite the
        ``rstcheck_config``;
        defaults to True
    :return: A list of found issues
    """
    run_config = _load_run_config(source_file.parent, rstcheck_config, overwrite_with_file_config)
    ignore_dict = _create_ignore_dict_from_config(run_config)
    _docutils.ignore_directives_and_roles(run_config.ignore_directives, run_config.ignore_roles)

    source = _get_source(source_file)
    source = _replace_ignored_substitutions(source, run_config.ignore_substitutions)

    all_errors = []
    for error in check_source(
        source,
        source_file=source_file,
        ignores=ignore_dict,
        report_level=run_config.report_level,
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
        defaults to True
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
        return sys.stdin.read()

    resolved_file_path = source_file.resolve()
    with contextlib.closing(docutils.io.FileInput(source_path=resolved_file_path)) as input_file:
        return typing.cast(str, input_file.read())


def _replace_ignored_substitutions(source: str, ignore_substitutions: typing.List[str]) -> str:
    """Replace rst substitutions from the ignore list with a dummy.

    :param source: Source to replace substitutions in
    :param ignore_substitutions: Substitutions to replace with dummy
    :return: Cleaned source
    """
    for substitution in ignore_substitutions:
        source = source.replace(f"|{substitution}|", f"x{substitution}x")
    return source


def _create_ignore_dict_from_config(rstcheck_config: config.RstcheckConfig) -> types.IgnoreDict:
    """Extract ignore settings from config and create a ``IgnoreDict``.

    :param rstcheck_config: Config to extract ignore settings from
    :return: ``IgnoreDict``
    """
    return types.IgnoreDict(
        messages=rstcheck_config.ignore_messages,
        languages=rstcheck_config.ignore_languages,
        directives=rstcheck_config.ignore_directives,
    )


def check_source(
    source: str,
    source_file: typing.Optional[pathlib.Path] = None,
    ignores: typing.Optional[types.IgnoreDict] = None,
    report_level: config.ReportLevel = config.ReportLevel.INFO,
) -> types.YieldedLintError:
    """Check the given rst source for issues.

    :param source_file: Path to file the source comes from if it comes from a file;
        defaults to None
    :param ignores: Ignore information; defaults to None
    :param report_level: Report level; defaults to config.ReportLevel.INFO
    :return: None
    :yield: Found issues
    """
    source_origin: types.SourceFileOrString = source_file or "<string>"
    ignores = ignores or types.IgnoreDict(messages=None, languages=[], directives=[])

    _docutils.register_code_directive(
        ignore_code_directive="code" in ignores["directives"],
        ignore_codeblock_directive="code-block" in ignores["directives"],
        ignore_sourcecode_directive="sourcecode" in ignores["directives"],
    )

    if _extras.SPHINX_INSTALLED:
        _sphinx.load_sphinx_ignores()

    try:
        ignores["languages"].extend(inline_config.find_ignored_languages(source))
    except inline_config.RstcheckCommentSyntaxError as error:
        yield types.LintError(
            source_origin=source_origin, line_number=error.line_number, message=f"{error}"
        )

    writer = _CheckWriter(source, source_origin, ignores, report_level)

    string_io = io.StringIO()

    # This is a hack to avoid false positive from docutils (#23). docutils
    # mistakes BOMs for actual visible letters. This results in the "underline
    # too short" warning firing.
    with contextlib.suppress(UnicodeError):
        source = source.encode("utf-8").decode("utf-8-sig")

    with contextlib.suppress(docutils.utils.SystemMessage, AttributeError):
        # Sphinx will sometimes throw an `AttributeError` trying to access
        # "self.state.document.settings.env". Ignore this for now until we
        # figure out a better approach.
        docutils.core.publish_string(
            source,
            writer=writer,
            source_path=str(source_origin),
            settings_overrides={
                "halt_level": 5,
                "report_level": report_level.value,
                "warning_stream": string_io,
            },
        )

    for checker in writer.checkers:
        yield from checker()

    rst_errors = string_io.getvalue().strip()

    if not rst_errors:
        return

    for message in rst_errors.splitlines():
        with contextlib.suppress(ValueError):
            if ignores["messages"] and ignores["messages"].search(message):
                continue
            yield _parse_gcc_style_error_message(
                message, source_origin=source_origin, has_column=False
            )


class _CheckWriter(docutils.writers.Writer):
    """Runs CheckTranslator on code blocks."""

    def __init__(
        self,
        source: str,
        source_origin: types.SourceFileOrString,
        ignores: typing.Optional[types.IgnoreDict] = None,
        report_level: config.ReportLevel = config.ReportLevel.INFO,
    ) -> None:
        """Inititalize _CheckWriter.

        :param source: Rst source to check
        :param source_origin: Path to file the source comes from
        :param ignores: Ignore information; defaults to None
        :param report_level: Report level; defaults to config.ReportLevel.INFO
        """
        docutils.writers.Writer.__init__(self)
        self.checkers: typing.List[types.CheckerRunFunction] = []
        self.source = source
        self.source_origin = source_origin
        self.ignores = ignores
        self.report_level = report_level

    def translate(self) -> None:
        """Run CheckTranslator."""
        visitor = _CheckTranslator(
            self.document,
            source=self.source,
            source_origin=self.source_origin,
            ignores=self.ignores,
            report_level=self.report_level,
        )
        self.document.walkabout(visitor)
        self.checkers += visitor.checkers


class _CheckTranslator(docutils.nodes.NodeVisitor):
    """Visits code blocks and checks for syntax errors in code."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        document: docutils.nodes.document,
        source: str,
        source_origin: types.SourceFileOrString,
        ignores: typing.Optional[types.IgnoreDict] = None,
        report_level: config.ReportLevel = config.ReportLevel.INFO,
    ) -> None:
        """Inititalize _CheckTranslator.

        :param document: Document node
        :param source: Rst source to check
        :param source_origin: Path to file the source comes from
        :param ignores: Ignore information; defaults to None
        :param report_level: Report level; defaults to config.ReportLevel.INFO
        """
        docutils.nodes.NodeVisitor.__init__(self, document)
        self.checkers: typing.List[types.CheckerRunFunction] = []
        self.source = source
        self.source_origin = source_origin
        self.ignores = ignores or types.IgnoreDict(messages=None, languages=[], directives=[])
        self.report_level = report_level
        self.code_block_checker = CodeBlockChecker(source_origin, ignores, report_level)

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
            if "code" in classes:
                language = classes[-1]
            else:
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


class CodeBlockChecker:
    """Checker for code blockes with different languages."""

    def __init__(
        self,
        source_origin: types.SourceFileOrString,
        ignores: typing.Optional[types.IgnoreDict] = None,
        report_level: config.ReportLevel = config.ReportLevel.INFO,
    ) -> None:
        """Inititalize CodeBlockChecker.

        :param source_origin: Path to file the source comes from
        :param ignores: Ignore information; defaults to None
        :param report_level: Report level; defaults to config.ReportLevel.INFO
        """
        self.source_origin = source_origin
        self.ignores = ignores
        self.report_level = report_level

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
        """Call the apropiate checker function for the given langauge to check given source.

        :param source: Source code to check
        :param language: Language of the source code
        :return: None if language is not supported
        :yield: Found issues
        """
        checker_function = typing.Callable[[str], types.YieldedLintError]
        checker: typing.Optional[checker_function] = getattr(self, f"check_{language}", None)
        if checker is None:
            return None

        yield from checker(source_code)
        return None

    def check_python(self, source_code: str) -> types.YieldedLintError:
        """Check python source for syntax errors.

        :param source: Python source code to check
        :return: None
        :yield: Found issues
        """
        try:
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
        :return: None
        :yield: Found issues
        """
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
        :return: None
        :yield: Found issues
        """
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
        :return: None
        :yield: Found issues
        """
        yield from check_source(
            source_code,
            source_file=None,
            ignores=self.ignores,
            report_level=self.report_level,
        )

    def check_doctest(self, source_code: str) -> types.YieldedLintError:
        """Check doctest source for syntax errors.

        This does not run the test as that would be unsafe. Nor does this
        check the Python syntax in the doctest. That could be purposely
        incorrect for testing purposes.

        :param source: XML source code to check
        :return: None
        :yield: Found issues
        """
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
        :return: None
        :yield: Found issues
        """
        result = self._run_in_subprocess(source_code, ".bash", ["bash", "-n"])

        if result:
            (output, filename) = result
            prefix = str(filename) + ": line "
            for line in output.splitlines():
                if not line.startswith(prefix):
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
        :return: None
        :yield: Found issues
        """
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
        :return: None
        :yield: Found issues
        """
        yield from self._gcc_checker(
            source_code,
            ".cpp",
            [os.getenv("CXX", "g++")]
            + shlex.split(os.getenv("CXXFLAGS", ""))
            + shlex.split(os.getenv("CPPFLAGS", ""))
            + ["-I.", "-I.."],
        )

    def _gcc_checker(
        self, source_code: str, filename_suffix: str, arguments: typing.List[str]
    ) -> types.YieldedLintError:
        """Check code blockes using gcc (Helper function).

        :param source_code: Source code to check
        :param filename_suffix: File suffix for language of the source code
        :param arguments: Command and arguments to run
        :return: None
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
        arguments: typing.List[str],
    ) -> typing.Optional[typing.Tuple[str, pathlib.Path]]:
        """Run checker in a subprocess (Helper function).

        :param source_code: Source code to check
        :param filename_suffix: File suffix for language of the source code
        :param arguments: Command and arguments to run
        :return: ``None`` if no issues were found else a tuple of the stderr and temp-file name
        """
        get_encoding = lambda: locale.getpreferredencoding() or sys.getdefaultencoding()

        source_origin_path = self.source_origin
        if isinstance(source_origin_path, str):
            source_origin_path = pathlib.Path(source_origin_path)

        with tempfile.NamedTemporaryFile(mode="wb", suffix=filename_suffix) as temporary_file:
            temporary_file.write(code.encode("utf-8"))
            temporary_file.flush()

            result = subprocess.run(  # pylint: disable=subprocess-run-check # noqa: S603
                arguments + [temporary_file.name],
                capture_output=True,
                cwd=source_origin_path.parent,
            )

            if result.returncode != 0:
                return (result.stderr.decode(get_encoding()), pathlib.Path(temporary_file.name))
            return None


def _parse_gcc_style_error_message(
    message: str, source_origin: types.SourceFileOrString, has_column: bool = True
) -> types.LintError:
    """Parse GCC-style error message.

    Return (line_number, message). Raise ValueError if message cannot be
    parsed.

    :param message: Message to parse
    :param filename: File the message is associated with
    :param has_column: The the message has a column number; defaults to True
    :raises ValueError: If the message cannot be parsed
    :return: Parsed message
    """
    colons = 2 if has_column else 1
    prefix = str(source_origin) + ":"
    if not message.startswith(prefix):
        raise ValueError("Message cannot be parsed.")
    message = message[len(prefix) :]
    split_message = message.split(":", colons)
    line_number = int(split_message[0])
    return types.LintError(
        source_origin=source_origin, line_number=line_number, message=split_message[colons].strip()
    )
