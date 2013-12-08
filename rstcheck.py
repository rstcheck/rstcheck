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


__version__ = '0.1.1'


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


class CheckTranslator(nodes.NodeVisitor):

    """Visits code blocks and checks for syntax errors in code."""

    def __init__(self, document, strict_warnings):
        nodes.NodeVisitor.__init__(self, document)
        self.strict_warnings = strict_warnings
        self.success = True

    def visit_literal_block(self, node):
        """Check syntax of code block."""
        if not node_has_class(node, 'code-block'):
            return

        language = node.get('language', None)

        error_flag = (['-Werror'] if self.strict_warnings else [])

        result = {
            'bash': ('.bash', ['bash', '-n']),
            'c': ('.c', ['gcc', '-fsyntax-only', '-O3', '-std=c99',
                         '-pedantic', '-Wall', '-Wextra'] + error_flag),
            'cpp': ('.cpp', ['g++', '-std=c++0x', '-pedantic', '-fsyntax-only',
                             '-O3', '-Wall', '-Wextra'] + error_flag),
            'python': ('.py', ['python', '-m', 'compileall'])
        }.get(language)

        green = '\x1b[32m'
        red = '\x1b[31m'
        end = '\x1b[0m'

        if result:
            (extension, arguments) = result

            output_file = tempfile.NamedTemporaryFile(mode='w',
                                                      suffix=extension)
            output_file.write(node.rawsource)
            output_file.flush()

            print(node.rawsource, file=sys.stderr)
            status = green + 'Okay' + end
            try:
                subprocess.check_call(arguments + [output_file.name])
            except subprocess.CalledProcessError:
                status = red + 'Error' + end
                self.success = False

            print(status, file=sys.stderr)
        else:
            print(red + 'Unknown language: {}'.format(language) + end,
                  file=sys.stderr)
            if self.strict_warnings:
                self.success = False

        raise nodes.SkipNode

    def unknown_visit(self, node):
        """Ignore."""

    def unknown_departure(self, node):
        """Ignore."""


class CheckWriter(writers.Writer):

    """Runs CheckTranslator on code blocks."""

    def __init__(self, strict_warnings):
        writers.Writer.__init__(self)
        self.strict_warnings = strict_warnings
        self.success = True

    def translate(self):
        """Run CheckTranslator."""
        visitor = CheckTranslator(self.document,
                                  strict_warnings=self.strict_warnings)
        self.document.walkabout(visitor)
        self.success &= visitor.success


def check(filename, strict_rst, strict_warnings):
    """Return True if no errors are found."""
    settings_overrides = {}
    if strict_rst:
        settings_overrides['halt_level'] = 1

    with open(filename) as input_file:
        contents = input_file.read()

    writer = CheckWriter(strict_warnings)
    try:
        core.publish_string(contents, writer=writer,
                            source_path=filename,
                            settings_overrides=settings_overrides)
    except utils.SystemMessage:
        return False

    return writer.success


def main():
    """Return 0 on success."""
    parser = argparse.ArgumentParser(description=__doc__, prog='rstcheck')
    parser.add_argument('files', nargs='+',
                        help='files to check')
    parser.add_argument('--strict-rst', action='store_true',
                        help='parse ReStructuredText more strictly')
    parser.add_argument('--strict-warnings', action='store_true',
                        help='treat warnings as errors')
    args = parser.parse_args()

    status = 0
    for filename in args.files:
        if not check(filename,
                     strict_rst=args.strict_rst,
                     strict_warnings=args.strict_warnings):
            status = 1

    return status


if __name__ == '__main__':
    sys.exit(main())
