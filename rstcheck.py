#!/usr/bin/env python

"""Checks code blocks in ReStructuredText."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import subprocess
import sys
import tempfile

from docutils import core, nodes, utils, writers
from docutils.parsers import rst


__version__ = '0.3.1'


RED = '\x1b[31m'
END = '\x1b[0m'


def error(text):
    """Return text colored with ANSI escapes."""
    if sys.stderr.isatty():
        text = RED + text + END

    print(text, file=sys.stderr)


def node_has_class(node, classes):
    """Return True if node has the specified class."""
    if not (issubclass(type(classes), list)):
        classes = [classes]
    for cname in classes:
        if cname in node['classes']:
            return True
    return False


class CodeBlockDirective(rst.Directive):

    """Code block directive."""

    has_content = True
    optional_arguments = 1

    def run(self):
        """Run directive."""
        try:
            language = self.arguments[0]
        except IndexError:
            language = ''
        code = '\n'.join(self.content)
        literal = nodes.literal_block(code, code)
        literal['classes'].append('code-block')
        literal['language'] = language
        return [literal]

rst.directives.register_directive('code-block', CodeBlockDirective)
rst.directives.register_directive('sourcecode', CodeBlockDirective)


def check_bash(code):
    """Return None on success."""
    result = run_in_subprocess(code, '.bash', ['bash', '-n'])
    if result:
        errors = []
        (output, filename) = result
        prefix = filename + ': line '
        for line in output.splitlines():
            if not line.startswith(prefix):
                continue
            message = line[len(prefix):]
            split_message = message.split(':', 1)
            errors.append((int(split_message[0]) - 1, split_message[1]))
        return errors


def check_c(code):
    """Return None on success."""
    return check_gcc(
        code,
        '.c',
        ['gcc', '-fsyntax-only', '-O3', '-std=c99', '-pedantic',
         '-Wall', '-Wextra'])


def check_cpp(code):
    """Return None on success."""
    return check_gcc(
        code,
        '.cpp',
        ['g++', '-std=c++0x', '-pedantic', '-fsyntax-only', '-O3',
         '-Wall', '-Wextra'])


def check_gcc(code, filename_suffix, arguments):
    """Return None on success."""
    result = run_in_subprocess(code, filename_suffix, arguments)
    if result:
        errors = []
        (output, filename) = result
        prefix = filename + ':'
        for line in output.splitlines():
            if not line.startswith(prefix):
                continue
            message = line[len(prefix):]
            split_message = message.split(':', 2)
            try:
                line_number = int(split_message[0])
            except ValueError:
                continue
            errors.append((line_number, split_message[2]))
        return errors


def check_python(code):
    """Return None on success."""
    try:
        compile(code, '<string>', 'exec')
    except SyntaxError as exception:
        return [
            (int(exception.lineno), exception.msg)
        ]


def run_in_subprocess(code, filename_suffix, arguments):
    """Return None on success."""
    temporary_file = tempfile.NamedTemporaryFile(mode='w',
                                              suffix=filename_suffix)
    temporary_file.write(code)
    temporary_file.flush()

    process = subprocess.Popen(arguments + [temporary_file.name],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    raw_result = process.communicate()
    if process.returncode != 0:
        return (raw_result[1].decode('utf-8'),
                temporary_file.name)


class CheckTranslator(nodes.NodeVisitor):

    """Visits code blocks and checks for syntax errors in code."""

    def __init__(self, document, contents, filename):
        nodes.NodeVisitor.__init__(self, document)
        self.summary = []
        self.contents = contents
        self.filename = filename

    def visit_literal_block(self, node):
        """Check syntax of code block."""
        if not node_has_class(node, 'code-block'):
            return

        language = node.get('language', None)

        checker = {
            'bash': check_bash,
            'c': check_c,
            'cpp': check_cpp,
            'python': check_python
        }.get(language)

        if checker:
            all_results = checker(node.rawsource)
            if all_results is None:
                self.summary.append(True)
            else:
                self.summary.append(False)
                for result in all_results:
                    error_offset = result[0] - 1

                    error(
                        '{}:{}: (ERROR/3) {}'.format(
                            self.filename,
                            beginning_of_code_block(node, self.contents) +
                            error_offset,
                            result[1]))

        raise nodes.SkipNode

    def unknown_visit(self, node):
        """Ignore."""

    def unknown_departure(self, node):
        """Ignore."""


def beginning_of_code_block(node, full_contents):
    """Return line number of beginning of code block."""
    # The offsets are wrong if the RST text has
    # multiple lines after the code block. This is a
    # workaround.
    lines = full_contents.splitlines()
    line_number = node.line
    for line_number in range(node.line, 1, -1):
        if lines[line_number - 2].strip():
            break

    return line_number - len(node.rawsource.splitlines())


class CheckWriter(writers.Writer):

    """Runs CheckTranslator on code blocks."""

    def __init__(self, contents, filename):
        writers.Writer.__init__(self)
        self.summary = []
        self.contents = contents
        self.filename = filename

    def translate(self):
        """Run CheckTranslator."""
        visitor = CheckTranslator(self.document,
                                  contents=self.contents,
                                  filename=self.filename)
        self.document.walkabout(visitor)
        self.summary += visitor.summary


def check(filename, report_level):
    """Return True if no errors are found."""
    settings_overrides = {'report_level': report_level}

    with open(filename) as input_file:
        contents = input_file.read()

    writer = CheckWriter(contents, filename)
    try:
        core.publish_string(contents, writer=writer,
                            source_path=filename,
                            settings_overrides=settings_overrides)
    except utils.SystemMessage:
        return False

    return writer.summary


def main():
    """Return 0 on success."""
    parser = argparse.ArgumentParser(description=__doc__, prog='rstcheck')
    parser.add_argument('files', nargs='+',
                        help='files to check')
    parser.add_argument('--report', type=int, metavar='level', default=2,
                        help='report system messages at or higher than level; '
                             '1 info, 2 warning, 3 error, 4 severe, 5 none '
                             '(default: %(default)s)')
    args = parser.parse_args()

    summary = []
    for filename in args.files:
        summary += check(filename,
                         report_level=args.report)

    failures = len([1 for value in summary if not value])
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
