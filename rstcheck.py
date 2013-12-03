#!/usr/bin/env python

"""Checks code blocks in ReStructuredText."""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import subprocess
import sys
import tempfile

from docutils import core
from docutils.writers import latex2e
from docutils import nodes
from docutils.parsers import rst


__version__ = '0.1'


def node_has_class(node, classes):
    """Return True if node has the specified class."""
    if not (issubclass(type(classes), list)):
        classes = [classes]
    for cname in classes:
        if cname in node['classes']:
            return True
    return False


class CodeBlockDirective(rst.Directive):

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = {
        'linenos': rst.directives.flag,
    }

    def run(self):
        try:
            language = self.arguments[0]
        except IndexError:
            language = 'guess'
        code = '\n'.join(self.content)
        literal = nodes.literal_block(code, code)
        literal['classes'].append('code-block')
        literal['language'] = language
        literal['linenos'] = 'linenos' in self.options
        return [literal]

for _name in ['code-block', 'sourcecode']:
    rst.directives.register_directive(_name, CodeBlockDirective)


# TODO: Use plain Translator.
class CheckTranslator(latex2e.LaTeXTranslator):

    def __init__(self, document):
        latex2e.LaTeXTranslator.__init__(self, document)
        self.success = True

    def visit_literal_block(self, node):
        if not node_has_class(node, 'code-block'):
            return

        language = node.get('language', None)

        extension = {
            'cpp': '.cpp',
            'python': '.py'
        }.get(language)

        output_file = tempfile.NamedTemporaryFile(mode='w', suffix=extension)
        output_file.write(node.rawsource)
        output_file.flush()

        print(node.rawsource, file=sys.stderr)
        status = '\x1b[32mOkay\x1b[0m'
        try:
            if language == 'cpp':
                subprocess.check_call(['g++', '-std=c++0x', '-fsyntax-only',
                                       '-O3', '-Wall', '-Wextra',
                                       output_file.name])
            elif language == 'python':
                subprocess.check_call(['python', '-m', 'compileall',
                                       output_file.name])
            else:
                print('Unknown language: {}'.format(language), file=sys.stderr)
        except subprocess.CalledProcessError:
            status = '\x1b[31mError\x1b[0m'
            self.success = False

        print(status)

        raise nodes.SkipNode

    def depart_literal_block(self, node):
        pass


# TODO: Use plain Writer.
class CheckWriter(latex2e.Writer):

    def __init__(self):
        latex2e.Writer.__init__(self)
        self.success = True

    def translate(self):
        visitor = CheckTranslator(self.document)
        self.document.walkabout(visitor)
        # copy parts
        for part in self.visitor_attributes:
            setattr(self, part, getattr(visitor, part))
        self.success &= visitor.success


def check(filename):
    with open(filename) as input_file:
        contents = input_file.read()

    writer = CheckWriter()
    core.publish_string(contents, writer=writer,
                   source_path=filename)
    return writer.success


def main():
    parser = argparse.ArgumentParser(description=__doc__, prog='rstcheck')
    parser.add_argument('files', nargs='+',
                        help='files to check')
    args = parser.parse_args()

    status = 0
    for filename in args.files:
        if not check(filename):
            status = 1

    return status


if __name__ == '__main__':
    sys.exit(main())
