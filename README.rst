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


Usage in Vim
============

To check reStructuredText in Vim using Syntastic_:

.. code-block:: vim

    let g:syntastic_rst_checkers = ['rstcheck']

.. _Syntastic: https://github.com/scrooloose/syntastic
