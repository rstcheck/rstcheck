#!/usr/bin/env python

# Copyright (C) 2013-2016 Steven Myint
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Checks code blocks in reStructuredText."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import contextlib
import doctest
import io
import json
import locale
import multiprocessing
import os
import re
import subprocess
import sys
import tempfile

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import docutils.core
import docutils.io
import docutils.nodes
import docutils.parsers.rst
import docutils.utils
import docutils.writers

import sphinx
import sphinx.directives
import sphinx.domains.c
import sphinx.domains.cpp
import sphinx.domains.javascript
import sphinx.domains.python
import sphinx.domains.std
import sphinx.roles


__version__ = '2.1'


SPHINX_CODE_BLOCK_DELTA = -1

RSTCHECK_COMMENT_RE = re.compile(r'\.\. rstcheck:')


class Error(Exception):

    """rstcheck exception."""

    def __init__(self, message, line_number):
        self.line_number = line_number
        Exception.__init__(self, message)


def check(source,
          filename='<string>',
          report_level=docutils.utils.Reporter.INFO_LEVEL,
          ignore=None,
          debug=False):
    """Yield errors.

    Use lower report_level for noisier error output.

    Each yielded error is a tuple of the form:

        (line_number, message)

    Line numbers are indexed at 1 and are with respect to the full RST file.

    Each code block is checked asynchronously in a subprocess.

    """
    ignore = ignore or []

    try:
        ignore.extend(find_ignored_languages(source))
    except Error as error:
        yield (error.line_number, '{}'.format(error))

    writer = CheckWriter(source, filename, ignore=ignore)

    string_io = io.StringIO()

    try:
        docutils.core.publish_string(
            source, writer=writer,
            source_path=filename,
            settings_overrides={'halt_level': report_level,
                                'report_level': report_level,
                                'warning_stream': string_io})
    except docutils.utils.SystemMessage:
        pass
    except AttributeError:
        # Sphinx will sometimes throw an exception trying to access
        # "self.state.document.settings.env". Ignore this for now until we
        # figure out a better approach.
        if debug:
            raise

    for checker in writer.checkers:
        for error in checker():
            yield error

    rst_errors = string_io.getvalue().strip()
    if rst_errors:
        for message in rst_errors.splitlines():
            try:
                yield parse_gcc_style_error_message(message,
                                                    filename=filename,
                                                    has_column=False)
            except ValueError:
                continue


def find_ignored_languages(source):
    """Yield ignored languages.

    Languages are ignored via comment.

    For example, to ignore C++, JSON, and Python:

    >>> list(find_ignored_languages('''
    ... Example
    ... =======
    ...
    ... .. rstcheck: ignore-language=cpp,json
    ...
    ... .. rstcheck: ignore-language=python
    ... '''))
    ['cpp', 'json', 'python']

    """
    for (index, line) in enumerate(source.splitlines()):
        match = RSTCHECK_COMMENT_RE.match(line)
        if match:
            key_and_value = line[match.end():].strip().split('=')
            if len(key_and_value) != 2:
                raise Error('Expected "key=value" syntax',
                            line_number=index + 1)

            if key_and_value[0] == 'ignore-language':
                for language in key_and_value[1].split(','):
                    yield language.strip()


def _check_file(parameters):
    """Return list of errors."""
    (filename, args) = parameters

    if filename == '-':
        contents = sys.stdin.read()
    else:
        with contextlib.closing(
                docutils.io.FileInput(source_path=filename)
        ) as input_file:
            contents = input_file.read()

    ignore_from_config(os.path.dirname(os.path.realpath(filename)))
    ignore_directives_and_roles(args.ignore_directives, args.ignore_roles)
    ignore_sphinx()
    for substitution in args.ignore_substitutions:
        contents = contents.replace('|{}|'.format(substitution), 'None')

    all_errors = []
    for error in check(contents,
                       filename=filename,
                       report_level=args.report,
                       ignore=args.ignore_language,
                       debug=args.debug):
        all_errors.append(error)
    return (filename, all_errors)


def check_python(code):
    """Yield errors."""
    try:
        compile(code, '<string>', 'exec')
    except SyntaxError as exception:
        yield (int(exception.lineno), exception.msg)


def check_json(code):
    """Yield errors."""
    try:
        json.loads(code)
    except ValueError as exception:
        message = '{}'.format(exception)
        line_number = 0

        found = re.search(r': line\s+([0-9]+)[^:]*$', message)
        if found:
            line_number = int(found.group(1))

        yield (int(line_number), message)


def check_rst(code, ignore):
    """Yield errors in nested RST code."""
    filename = '<string>'

    for result in check(code,
                        filename=filename,
                        ignore=ignore):
        yield result


def check_doctest(code):
    """Yield doctest syntax errors.

    This does not run the test as that would be unsafe. Nor does this
    check the Python syntax in the doctest. That could be purposely
    incorrect for testing purposes.

    """
    parser = doctest.DocTestParser()
    try:
        parser.parse(code)
    except ValueError as exception:
        message = '{}'.format(exception)
        match = re.match('line ([0-9]+)', message)
        if match:
            yield (int(match.group(1)), message)


def _get_directives_and_roles_from_config(path):
    """Return a tuple of Sphinx directive and roles."""
    parser = configparser.ConfigParser()
    parser.read(path)

    try:
        options = dict(parser.items('rstcheck'))
    except configparser.NoSectionError:
        options = {}

    directives = get_and_split(options, 'ignore_directives')
    roles = get_and_split(options, 'ignore_roles')

    return (directives, roles)


def get_and_split(options, key):
    """Return list of split and stripped strings."""
    return split_comma_separated(options.get(key, ''))


def split_comma_separated(text):
    """Return list of split and stripped strings."""
    return [t.strip() for t in text.split(',') if t.strip()]


def _get_directives_and_roles_from_sphinx():
    """Return a tuple of Sphinx directive and roles."""
    sphinx_directives = list(sphinx.domains.std.StandardDomain.directives)
    sphinx_roles = list(sphinx.domains.std.StandardDomain.roles)

    for domain in [sphinx.domains.c.CDomain,
                   sphinx.domains.cpp.CPPDomain,
                   sphinx.domains.javascript.JavaScriptDomain,
                   sphinx.domains.python.PythonDomain]:

        sphinx_directives += list(domain.directives) + [
            '{}:{}'.format(domain.name, item)
            for item in list(domain.directives)]

        sphinx_roles += list(domain.roles) + [
            '{}:{}'.format(domain.name, item)
            for item in list(domain.roles)]

    return (sphinx_directives, sphinx_roles)


class IgnoredDirective(docutils.parsers.rst.Directive):

    """Stub for unknown directives."""

    has_content = True

    def run(self):
        """Do nothing."""
        return []


def _ignore_role(name, rawtext, text, lineno, inliner,
                 options=None, content=None):
    """Stub for unknown roles."""
    # pylint: disable=unused-argument
    return ([], [])


def ignore_sphinx():
    """Register Sphinx directives and roles to ignore."""
    (directives, roles) = _get_directives_and_roles_from_sphinx()

    directives += [
        'centered',
        'include',
        'deprecated',
        'index',
        'no-code-block',
        'literalinclude',
        'hlist',
        'seealso',
        'toctree',
        'todo',
        'versionadded',
        'versionchanged']

    ext_autosummary = [
        'autosummary',
        'currentmodule',
    ]

    ignore_directives_and_roles(directives + ext_autosummary,
                                roles + ['ctype'])


def find_config(directory):
    """Return configuration filename.

    Find configuration in directory or its ancestor.

    """
    directory = os.path.realpath(directory)

    while directory:
        candidate = os.path.join(directory, '.rstcheck.cfg')
        if os.path.exists(candidate):
            return candidate

        parent_directory = os.path.dirname(directory)
        if parent_directory == directory:
            break
        else:
            directory = parent_directory


def ignore_from_config(directory):
    """Ignore directives/roles based on a configuration file.

    Find configuration in directory or its ancestor.

    """
    config_path = find_config(directory)
    if not config_path:
        return

    ignore_directives_and_roles(
        *_get_directives_and_roles_from_config(config_path))


def ignore_directives_and_roles(directives, roles):
    """Ignore directives/roles in docutils."""
    for directive in directives:
        docutils.parsers.rst.directives.register_directive(directive,
                                                           IgnoredDirective)

    for role in roles:
        docutils.parsers.rst.roles.register_local_role(role, _ignore_role)


# The checker functions below return a checker. This is for purposes of
# asynchronous checking. As we visit each code block, a subprocess gets
# launched to run the checker. They all run in the background until we finish
# traversing the document. At that point, we accumulate the errors.


def bash_checker(code, working_directory):
    """Return checker."""
    run = run_in_subprocess(code, '.bash', ['bash', '-n'],
                            working_directory=working_directory)

    def run_check():
        """Yield errors."""
        result = run()
        if result:
            (output, filename) = result
            prefix = filename + ': line '
            for line in output.splitlines():
                if not line.startswith(prefix):
                    continue
                message = line[len(prefix):]
                split_message = message.split(':', 1)
                yield (int(split_message[0]) - 1,
                       split_message[1].strip())
    return run_check


def c_checker(code, working_directory):
    """Return checker."""
    return gcc_checker(code, '.c', [os.getenv('CC', 'gcc'), '-std=c99', '-I.'],
                       working_directory=working_directory)


def cpp_checker(code, working_directory):
    """Return checker."""
    return gcc_checker(code, '.cpp', [os.getenv('CXX', 'g++'), '-std=c++0x',
                                      '-I.'],
                       working_directory=working_directory)


def gcc_checker(code, filename_suffix, arguments, working_directory):
    """Return checker."""
    run = run_in_subprocess(code,
                            filename_suffix,
                            arguments + ['-pedantic', '-fsyntax-only'],
                            working_directory=working_directory)

    def run_check():
        """Yield errors."""
        result = run()
        if result:
            (output, filename) = result
            for line in output.splitlines():
                try:
                    yield parse_gcc_style_error_message(line,
                                                        filename=filename)
                except ValueError:
                    continue

    return run_check


def parse_gcc_style_error_message(message, filename, has_column=True):
    """Parse GCC-style error message.

    Return (line_number, message). Raise ValueError if message cannot be
    parsed.

    """
    colons = 2 if has_column else 1
    prefix = filename + ':'
    if not message.startswith(prefix):
        raise ValueError()
    message = message[len(prefix):]
    split_message = message.split(':', colons)
    line_number = int(split_message[0])
    return (line_number,
            split_message[colons].strip())


def get_encoding():
    """Return preferred encoding."""
    return locale.getpreferredencoding() or sys.getdefaultencoding()


def run_in_subprocess(code, filename_suffix, arguments, working_directory):
    """Return None on success."""
    temporary_file = tempfile.NamedTemporaryFile(mode='wb',
                                                 suffix=filename_suffix)
    temporary_file.write(code.encode('utf-8'))
    temporary_file.flush()

    process = subprocess.Popen(arguments + [temporary_file.name],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               cwd=working_directory)

    def run():
        """Yield errors."""
        raw_result = process.communicate()
        if process.returncode != 0:
            return (raw_result[1].decode(get_encoding()),
                    temporary_file.name)

    return run


class CheckTranslator(docutils.nodes.NodeVisitor):

    """Visits code blocks and checks for syntax errors in code."""

    def __init__(self, document, contents, filename, ignore):
        docutils.nodes.NodeVisitor.__init__(self, document)
        self.checkers = []
        self.contents = contents
        self.filename = filename
        self.working_directory = os.path.dirname(os.path.realpath(filename))
        self.ignore = ignore or []
        self.ignore.append(None)

    def visit_doctest_block(self, node):
        """Check syntax of doctest."""
        if 'doctest' in self.ignore:
            return

        self._add_check(node=node,
                        run=lambda: check_doctest(node.rawsource),
                        language='doctest')

    def visit_literal_block(self, node):
        """Check syntax of code block."""
        # For "..code-block:: language"
        language = node.get('language', None)
        if language in self.ignore:
            # For "..code:: language"
            classes = node.get('classes')
            if 'code' in classes:
                language = classes[-1]
            else:
                return

        if language == 'doctest' or (
                language == 'python' and
                node.rawsource.lstrip().startswith('>>> ')):
            self.visit_doctest_block(node)
            raise docutils.nodes.SkipNode

        checker = {
            'bash': bash_checker,
            'c': c_checker,
            'cpp': cpp_checker,
            'json': lambda source, _: lambda: check_json(source),
            'python': lambda source, _: lambda: check_python(source),
            'rst': lambda source, _: lambda: check_rst(source,
                                                       ignore=self.ignore)
        }.get(language)

        if checker:
            run = checker(node.rawsource, self.working_directory)
            self._add_check(node=node, run=run, language=language)

        raise docutils.nodes.SkipNode

    def _add_check(self, node, run, language):
        """Add checker that will be run."""
        def run_check():
            """Yield errors."""
            all_results = run()
            if all_results is not None:
                if all_results:
                    for result in all_results:
                        error_offset = result[0] - 1

                        try:
                            yield (
                                beginning_of_code_block(node, self.contents) +
                                error_offset,
                                '({}) {}'.format(language, result[1]))
                        except TypeError:
                            # Ignore case where node's line_number is None.
                            pass
                else:
                    yield (self.filename, 0, 'unknown error')
        self.checkers.append(run_check)

    def unknown_visit(self, node):
        """Ignore."""

    def unknown_departure(self, node):
        """Ignore."""


def beginning_of_code_block(node, full_contents):
    """Return line number of beginning of code block."""
    line_number = node.line
    delta = len(node.non_default_attributes())
    current_line_contents = full_contents.splitlines()[line_number:]
    blank_lines = next((i for (i, x) in enumerate(current_line_contents) if x),
                       0)
    return line_number + delta - 1 + blank_lines - 1 + SPHINX_CODE_BLOCK_DELTA


class CheckWriter(docutils.writers.Writer):

    """Runs CheckTranslator on code blocks."""

    def __init__(self, contents, filename, ignore):
        docutils.writers.Writer.__init__(self)
        self.checkers = []
        self.contents = contents
        self.filename = filename
        self.ignore = ignore

    def translate(self):
        """Run CheckTranslator."""
        visitor = CheckTranslator(self.document,
                                  contents=self.contents,
                                  filename=self.filename,
                                  ignore=self.ignore)
        self.document.walkabout(visitor)
        self.checkers += visitor.checkers


def decode_filename(filename):
    """Return Unicode filename."""
    if hasattr(filename, 'decode'):
        return filename.decode(sys.getfilesystemencoding())
    else:
        return filename


def parse_args():
    """Return parsed command-line arguments."""
    threshold_choices = docutils.frontend.OptionParser.threshold_choices

    parser = argparse.ArgumentParser(description=__doc__, prog='rstcheck')
    parser.add_argument('files', nargs='+', type=decode_filename,
                        help='files to check')
    parser.add_argument('--report', metavar='level',
                        choices=threshold_choices,
                        default='info',
                        help='report system messages at or higher than '
                             'level; ' +
                             ', '.join(choice for choice in threshold_choices
                                       if not choice.isdigit()) +
                             ' (default: %(default)s)')
    parser.add_argument('--ignore-language', '--ignore',
                        metavar='language', default='',
                        help='comma-separated list of languages to ignore')
    parser.add_argument('--ignore-directives',
                        metavar='directives', default='',
                        help='comma-separated list of directives to ignore')
    parser.add_argument('--ignore-substitutions',
                        metavar='substitutions', default='',
                        help='comma-separated list of substitutions to ignore')
    parser.add_argument('--ignore-roles',
                        metavar='roles', default='',
                        help='comma-separated list of roles to ignore')
    parser.add_argument('--debug', action='store_true',
                        help='show helpful for debugging')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + __version__)
    args = parser.parse_args()

    if '-' in args.files and len(args.files) > 1:
        parser.error("'-' for standard in can only be checked alone")

    args.ignore_language = split_comma_separated(args.ignore_language)
    args.ignore_directives = split_comma_separated(args.ignore_directives)
    args.ignore_roles = split_comma_separated(args.ignore_roles)
    args.ignore_substitutions = split_comma_separated(
        args.ignore_substitutions
    )

    threshold_dictionary = docutils.frontend.OptionParser.thresholds
    args.report = int(threshold_dictionary.get(args.report, args.report))

    return args


def output_message(text, file=sys.stderr):
    """Output message to terminal."""
    if file.encoding is None:
        # If the output file does not support Unicode, encode it to a byte
        # string. On some machines, this occurs when Python is redirecting to
        # file (or piping to something like Vim).
        text = text.encode('utf-8')

    print(text, file=file)


def main():
    """Return 0 on success."""
    args = parse_args()

    status = 0
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    try:
        if len(args.files) > 1:
            # Run in separate process to avoid mutating the global docutils
            # settings based on the local configuration. It also avoids
            # mutating the settings when rstcheck is used as a module.
            results = pool.map(
                _check_file,
                [(name, args) for name in args.files])
        else:
            # This is for the case where we read from standard in.
            results = [_check_file((args.files[0], args))]

        for (filename, errors) in results:
            for error in errors:
                line_number = error[0]
                message = error[1]

                if not re.match(r'\([A-Z]+/[0-9]+\)', message):
                    message = '(ERROR/3) ' + message

                output_message('{}:{}: {}'.format(filename,
                                                  line_number,
                                                  message))

                status = 1
    except (IOError, UnicodeError) as exception:
        output_message(exception)
        status = 1

    return status


if __name__ == '__main__':
    sys.exit(main())
