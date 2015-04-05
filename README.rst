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

    usage: rstcheck [-h] [--report level] [--ignore language] files [files ...]

    Checks code blocks in reStructuredText.

    positional arguments:
      files              files to check

    optional arguments:
      -h, --help         show this help message and exit
      --report level     report system messages at or higher than level; 1 info, 2
                         warning, 3 error, 4 severe, 5 none (default: 1)
      --ignore language  comma-separated list of languages to ignore


Ignore languages
================

You can ignore checking of nested code blocks by language. Either use the
command-line option ``--ignore`` or put a comment in the document:

.. code-block:: rst

    .. rstcheck: ignore-language=cpp,python,rst


Configuration
=============

If your project has custom roles and directives, you can specify them in the
local configuration of the project. ``rstcheck`` looks for a file
``.rstcheck.cfg`` in the directory where it was launched.

For example, consider a project with the following directory structure::

    docs
    ├── foo
    │   └── bar.rst
    ├── index.rst
    └── .rstcheck.cfg

``.rstcheck.cfg`` contains:

.. code-block:: cfg

    [roles]
    ignore=src,RFC

    [directives]
    ignore=one,two,three

``bar.rst`` contains:

.. code-block:: rst

    Bar
    ===

    :src:`hello_world.py`
    :RFC:`793`

    .. one::

       Hello

``rstcheck`` will consider the ``.rstcheck.cfg`` if run from the appropriate
directory::

    $ cd docs
    $ rstcheck foo/bar.rst


Usage in Vim
============

To check reStructuredText in Vim using Syntastic_:

.. code-block:: vim

    let g:syntastic_rst_checkers = ['rstcheck']

.. _Syntastic: https://github.com/scrooloose/syntastic


Use as a module
===============

>>> import rstcheck
>>> list(rstcheck.check('Example\n==='))
[(2, '(INFO/1) Possible title underline, too short for the title.')]

.. rstcheck: ignore-language=cpp,python,rst
