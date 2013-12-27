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


__version__ = '0.2'


GREEN = '\x1b[32m'
RED = '\x1b[31m'


def inform(text, color):
    """Return text colored with ANSI escapes."""
    if sys.stderr.isatty():
        end = '\x1b[0m'
        text = color + text + end

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
            errors.append((int(split_message[0]) - 2, split_message[1]))
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

    def __init__(self, document, filename):
        nodes.NodeVisitor.__init__(self, document)
        self.summary = []
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
                    inform(
                        '{}:{}: {}'.format(
                            self.filename,
                            node.line + result[0] -
                            len(node.rawsource.splitlines()),
                            result[1]),
                        RED)
        else:
            inform('Unknown language: {}'.format(language), RED)

        raise nodes.SkipNode

    def unknown_visit(self, node):
        """Ignore."""

    def unknown_departure(self, node):
        """Ignore."""


class CheckWriter(writers.Writer):

    """Runs CheckTranslator on code blocks."""

    def __init__(self, filename):
        writers.Writer.__init__(self)
        self.summary = []
        self.filename = filename

    def translate(self):
        """Run CheckTranslator."""
        visitor = CheckTranslator(self.document,
                                  filename=self.filename)
        self.document.walkabout(visitor)
        self.summary += visitor.summary


def check(filename, strict_rst):
    """Return True if no errors are found."""
    settings_overrides = {}
    if strict_rst:
        settings_overrides['halt_level'] = 1

    with open(filename) as input_file:
        contents = input_file.read()

    writer = CheckWriter(filename)
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
    parser.add_argument('--strict-rst', action='store_true',
                        help='parse ReStructuredText more strictly')
    args = parser.parse_args()

    summary = []
    for filename in args.files:
        summary += check(filename,
                         strict_rst=args.strict_rst)

    failures = len([1 for value in summary if not value])
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
