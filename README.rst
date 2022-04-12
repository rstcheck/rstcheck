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

    usage: rstcheck [-h] [--config CONFIG] [-r] [--report level]
                    [--ignore-language language] [--ignore-messages messages]
                    [--ignore-directives directives]
                    [--ignore-substitutions substitutions] [--ignore-roles roles]
                    [--debug] [--version]
                    files [files ...]

    Checks code blocks in reStructuredText. Sphinx is enabled.

    positional arguments:
      files                 files to check

    optional arguments:
      -h, --help            show this help message and exit
      --config CONFIG       location of config file
      -r, --recursive       run recursively over directories
      --report level        report system messages at or higher than level; info,
                            warning, error, severe, none (default: info)
      --ignore-language language, --ignore language
                            comma-separated list of languages to ignore
      --ignore-messages messages
                            python regex that match the messages to ignore
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

Ignore specific errors
======================

Since docutils doesn't categorize their error messages beyond the high-level
categories of: info, warning, error, and severe; we need filter them out at a
textual level. This is done by passing a Python regex. As example you can pass
a regex like this to ignore several errors::

    (Title underline too short.*|Duplicate implicit target.*')

Configuration file
==================

You can use the same arguments from the command line as options in the
local configuration file of the project (just replace ``-`` for ``_``).
``rstcheck`` looks for a file ``.rstcheck.cfg`` or ``setup.cfg`` in the
directory or ancestor directories of the file it is checking.

For example, consider a project with the following directory structure::

    foo
    ├── docs
    │   └── bar.rst
    ├── index.rst
    └── .rstcheck.cfg

``.rstcheck.cfg`` contains:

.. code-block:: cfg

    [rstcheck]
    ignore_directives=one,two,three
    ignore_roles=src,RFC
    ignore_messages=(Document or section may not begin with a transition\.$)
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

    $ rstcheck foo/docs/bar.rst


For a Python project, you should put the configuration settings for
``rstcheck`` inside the general ``setup.cfg`` `distutils configuration file`_,
in the project root.

You can override the location of the config file with the ``--config`` argument::

    $ rstcheck --config $HOME/.rstcheck.ini foo/docs/bar.rst

will use the file ``.rstcheck.ini`` in your home directory. If the argument to
``--config`` is a directory, ``rstcheck`` will search that directory and any
any of its ancestors for a file ``.rstcheck.cfg`` or ``setup.cfg``::

   $ rstcheck --config foo /tmp/bar.rst

would use the project configuration in ``./foo/.rstcheck.cfg`` to check the
unrelated file ``/tmp/bar.rst``.
Calling ``rstcheck`` with the ``--debug`` option will show the location of the
config file that is being used, if any.

.. _distutils configuration file: https://docs.python.org/3/distutils/configfile.html


Sphinx
======

To enable Sphinx::

    $ pip install sphinx

The installed Sphinx version must be at least 1.5.

To check that Sphinx support is enabled::

    $ rstcheck -h | grep 'Sphinx is enabled'


Usage in Vim
============

Using with Syntastic_:
----------------------

.. code:: vim

    let g:syntastic_rst_checkers = ['rstcheck']

Using with ALE_:
----------------

Just install ``rstcheck`` and make sure is on your path.

.. _Syntastic: https://github.com/scrooloose/syntastic
.. _ALE: https://github.com/w0rp/ale


Use as a module
===============

``rstcheck.check()`` yields a series of tuples. The first value of each tuple
is the line number (not the line index). The second value is the error message.

>>> import rstcheck
>>> list(rstcheck.check('Example\n==='))
[(2, '(INFO/1) Possible title underline, too short for the title.')]

Note that this does not load any configuration as that would mutate the
``docutils`` registries.

Use as a pre-commit hook
========================

Add this to your ``.pre-commit-config.yaml``

.. code-block:: yaml

    -   repo: https://github.com/myint/rstcheck
        rev: ''  # Use the sha / tag you want to point at
        hooks:
        -   id: rstcheck

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

(next version)
--------------

3.4.0 (2022-04-12)
------------------

- Add ``--config`` option to change the location of the config file.
- Add ``pre-commit`` hooks config.

3.3.1 (2018-10-09)
------------------

- Make compatible with Sphinx >= 1.8.

3.3 (2018-03-17)
----------------

- Parse more options from configuration file (thanks to Santos Gallegos).
- Allow ignoring specific (info/warning/error) messages via
  ``--ignore-messages`` (thanks to Santos Gallegos).

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
