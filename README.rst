========
rstcheck
========

.. image:: https://travis-ci.org/myint/rstcheck.svg?branch=master
    :target: https://travis-ci.org/myint/rstcheck
    :alt: Build status

Checks syntax of reStructuredText and code blocks nested within it.


.. contents::


Installation
============

From pip::

    $ pip install rstcheck


Supported languages in code blocks
==================================

- Bash
- Doctest
- C (C99)
- C++ (C++11)
- JSON
- XML
- Python
- reStructuredText


Examples
========

With bad Python syntax:

.. code:: rst

    ====
    Test
    ====

    .. code:: python

        print(

::

    $ rstcheck bad_python.rst
    bad_python.rst:7: (ERROR/3) (python) unexpected EOF while parsing

With bad C++ syntax:

.. code:: rst

    ====
    Test
    ====

    .. code:: cpp

        int main()
        {
            return x;
        }

::

    $ rstcheck bad_cpp.rst
    bad_cpp.rst:9: (ERROR/3) (cpp) error: 'x' was not declared in this scope

With bad syntax in the reStructuredText document itself:

.. code:: rst

    ====
    Test
    ===

::

    $ rstcheck bad_rst.rst
    bad_rst.rst:1: (SEVERE/4) Title overline & underline mismatch.


Options
=======

::

    usage: rstcheck [-h] [-r] [--report level] [--ignore-language language]
                    [--ignore-directives directives]
                    [--ignore-substitutions substitutions] [--ignore-roles roles]
                    [--debug] [--version]
                    files [files ...]

    Checks code blocks in reStructuredText.

    positional arguments:
      files                 files to check

    optional arguments:
      -h, --help            show this help message and exit
      -r, --recursive       run recursively over directories
      --report level        report system messages at or higher than level; info,
                            warning, error, severe, none (default: info)
      --ignore-language language, --ignore language
                            comma-separated list of languages to ignore
      --ignore-directives directives
                            comma-separated list of directives to ignore
      --ignore-substitutions substitutions
                            comma-separated list of substitutions to ignore
      --ignore-roles roles  comma-separated list of roles to ignore
      --debug               show messages helpful for debugging
      --version             show program's version number and exit


Ignore specific languages
=========================

You can ignore checking of nested code blocks by language. Either use the
command-line option ``--ignore`` or put a comment in the document:

.. code-block:: rst

    .. rstcheck: ignore-language=cpp,python,rst


Configuration file
==================

You can use the same arguments from the command line as options in the
local configuration file of the project (just replace ``-`` for ``_``).
``rstcheck`` looks for a file ``.rstcheck.cfg`` in the directory or
ancestor directory of the file it is checking.

For example, consider a project with the following directory structure::

    docs
    ├── foo
    │   └── bar.rst
    ├── index.rst
    └── .rstcheck.cfg

``.rstcheck.cfg`` contains:

.. code-block:: cfg

    [rstcheck]
    ignore_directives=one,two,three
    ignore_roles=src,RFC
    report=warning

``bar.rst`` contains:

.. code-block:: rst

    Bar
    ===

    :src:`hello_world.py`
    :RFC:`793`

    .. one::

       Hello

``rstcheck`` will make use of the ``.rstcheck.cfg``::

    $ rstcheck docs/foo/bar.rst


Sphinx
======

To enable Sphinx::

    $ pip install sphinx

The installed Sphinx version must be at least 1.5.

To check that Sphinx support is enabled::

    $ rstcheck -h | grep 'Sphinx is enabled'


Usage in Vim
============

To check reStructuredText in Vim using Syntastic_:

.. code:: vim

    let g:syntastic_rst_checkers = ['rstcheck']

.. _Syntastic: https://github.com/scrooloose/syntastic


Use as a module
===============

``rstcheck.check()`` yields a series of tuples. The first value of each tuple
is the line number (not the line index). The second value is the error message.

>>> import rstcheck
>>> list(rstcheck.check('Example\n==='))
[(2, '(INFO/1) Possible title underline, too short for the title.')]

Note that this does not load any configuration as that would mutate the
``docutils`` registries.


Testing
=======

To run all the tests, do::

    $ make test

Unit tests are in ``test_rstcheck.py``.

System tests are composed of example good/bad input. The test inputs are
contained in the ``examples`` directory. For basic tests, adding a test should
just be a matter of adding files to ``examples/good`` or ``examples/bad``.


History
=======

3.2 (2018-02-17)
----------------

- Check for invalid Markdown-style links (thanks to biscuitsnake).
- Allow configuration to be stored in ``setup.cfg`` (thanks to Maël Pedretti).
- Add ``--recursive`` option to recursively drill down directories to check for
  all ``*.rst`` files.

3.1 (2017-03-08)
----------------

- Add support for checking XML code blocks (thanks to Sameer Singh).

3.0.1 (2017-03-01)
------------------

- Support UTF-8 byte order marks (BOM). Previously, ``docutils`` would
  interpret the BOM as a visible character, which would lead to false positives
  about underlines being too short.

3.0 (2016-12-19)
----------------

- Optionally support Sphinx 1.5. Sphinx support will be enabled if Sphinx is
  installed.

2.0 (2015-07-27)
----------------

- Support loading settings from configuration files.

1.0 (2015-03-14)
----------------

- Add Sphinx support.

0.1 (2013-12-02)
----------------

- Initial version.


.. rstcheck: ignore-language=cpp,python,rst
