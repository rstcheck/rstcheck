========
rstcheck
========

.. image:: https://travis-ci.org/myint/rstcheck.svg?branch=master
    :target: https://travis-ci.org/myint/rstcheck
    :alt: Build status

Checks syntax of reStructuredText and code blocks nested within it.


Installation
============

From pip::

    $ pip install --upgrade rstcheck


Supported languages in code blocks
==================================

- Bash
- Doctest
- C (C99)
- C++ (C++11)
- JSON
- Python
- reStructuredText


Examples
========

With bad Python syntax:

.. code-block:: rst

    ====
    Test
    ====

    .. code-block:: python

        print(

::

    $ rstcheck bad_python.rst
    bad_python.rst:7: (ERROR/3) (python) unexpected EOF while parsing

With bad C++ syntax:

.. code-block:: rst

    ====
    Test
    ====

    .. code-block:: cpp

        int main()
        {
            return x;
        }

::

    $ rstcheck bad_cpp.rst
    bad_cpp.rst:9: (ERROR/3) (cpp) error: 'x' was not declared in this scope

With bad syntax in the reStructuredText document itself:

.. code-block:: rst

    ====
    Test
    ===

::

    $ rstcheck bad_rst.rst
    bad_rst.rst:1: (SEVERE/4) Title overline & underline mismatch.


Options
=======

::

    usage: rstcheck [-h] [--report level] [--ignore-language language]
                    [--ignore-directives directives]
                    [--ignore-substitutions substitutions] [--ignore-roles roles]
                    [--debug] [--version]
                    files [files ...]

    Checks code blocks in reStructuredText.

    positional arguments:
      files                 files to check

    optional arguments:
      -h, --help            show this help message and exit
      --report level        report system messages at or higher than level; info,
                            warning, error, severe, none (default: info)
      --ignore-language language, --ignore language
                            comma-separated list of languages to ignore
      --ignore-directives directives
                            comma-separated list of directives to ignore
      --ignore-substitutions substitutions
                            comma-separated list of substitutions to ignore
      --ignore-roles roles  comma-separated list of roles to ignore
      --debug               show helpful for debugging
      --version             show program's version number and exit

Ignore specific languages
=========================

You can ignore checking of nested code blocks by language. Either use the
command-line option ``--ignore`` or put a comment in the document:

.. code-block:: rst

    .. rstcheck: ignore-language=cpp,python,rst


Configuration
=============

If your project has custom roles and directives, you can specify them in the
local configuration of the project. ``rstcheck`` looks for a file
``.rstcheck.cfg`` in the directory or ancestor directory of the file it is
checking.

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


Usage in Vim
============

To check reStructuredText in Vim using Syntastic_:

.. code-block:: vim

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

.. rstcheck: ignore-language=cpp,python,rst
