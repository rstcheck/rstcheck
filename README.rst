========
rstcheck
========

.. image:: https://github.com/myint/rstcheck/workflows/Test%20code/badge.svg?branch=master
    :target: https://github.com/myint/rstcheck/actions/workflows/test.yaml
    :alt: Test status

.. image:: https://github.com/myint/rstcheck/workflows/QA/badge.svg?branch=master
    :target: https://github.com/myint/rstcheck/actions/workflows/qa.yaml
    :alt: QA status

Checks syntax of reStructuredText and code blocks nested within it.


.. contents::


Installation
============

From pip

.. code:: shell

    $ pip install rstcheck

To use pyproject.toml for configuration::

    $ pip install rstcheck[toml]

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

.. code:: text

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

.. code:: text

    $ rstcheck bad_cpp.rst
    bad_cpp.rst:9: (ERROR/3) (cpp) error: 'x' was not declared in this scope

With bad syntax in the reStructuredText document itself:

.. code:: rst

    ====
    Test
    ===

.. code:: text

    $ rstcheck bad_rst.rst
    bad_rst.rst:1: (SEVERE/4) Title overline & underline mismatch.


Options
=======

.. code:: text

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

.. code:: rst

    .. rstcheck: ignore-language=cpp,python,rst


Ignore specific errors
======================

Since docutils doesn't categorize their error messages beyond the high-level
categories of: info, warning, error, and severe; we need filter them out at a
textual level. This is done by passing a Python regex. As example you can pass
a regex like this to ignore several errors

.. code:: text

    (Title underline too short.*|Duplicate implicit target.*')


Configuration file
==================

You can use the same arguments from the command line as options in the
local configuration file of the project (just replace ``-`` for ``_``).
``rstcheck`` looks for a file ``.rstcheck.cfg``, ``setup.cfg``, or
``pyproject.toml`` in the directory or ancestor directories of the file it is
checking.

``.rstcheck.cfg`` takes precedence over ``setup.cfg``.

Settings in the config file are overwritten by CLI options.

For example, consider a project with the following directory structure

.. code:: text

    foo
    ├── docs
    │   └── bar.rst
    ├── index.rst
    └── .rstcheck.cfg

``.rstcheck.cfg`` contains:

.. code:: ini

    [rstcheck]
    ignore_directives=one,two,three
    ignore_roles=src,RFC
    ignore_messages=(Document or section may not begin with a transition\.$)
    report=warning

``bar.rst`` contains:

.. code:: rst

    Bar
    ===

    :src:`hello_world.py`
    :RFC:`793`

    .. one::

       Hello

``rstcheck`` will make use of the ``.rstcheck.cfg``

.. code:: shell

    $ rstcheck foo/docs/bar.rst


For a Python project, you should put the configuration settings for
``rstcheck`` inside the general ``setup.cfg`` `distutils configuration file`_,
in the project root.

For a PEP-517/PEP-518 project, you should put the configuration settings for
``rstcheck`` inside the ``pyproject.toml`` configuration file in the project
root.  These should be placed in a ``[tool.rstcheck]`` section.  Keep in mind
backslashes need to be escaped, so to ignore the message
``"(Document or section may not begin with a transition\.$)"`` you'll need to
escape the backslash in ``pyproject.toml`` like this
``"(Document or section may not begin with a transition\\.$)"``.  See the
``pyproject.toml`` file in ``examples/with_configuration``.

You can override the location of the config file with the ``--config`` argument

.. code:: shell

    $ rstcheck --config $HOME/.rstcheck.ini foo/docs/bar.rst

will use the file ``.rstcheck.ini`` in your home directory. If the argument to
``--config`` is a directory, ``rstcheck`` will search that directory and any
any of its ancestors for a file ``.rstcheck.cfg`` or ``setup.cfg``

.. code:: shell

   $ rstcheck --config foo /tmp/bar.rst

would use the project configuration in ``./foo/.rstcheck.cfg`` to check the
unrelated file ``/tmp/bar.rst``.
Calling ``rstcheck`` with the ``--debug`` option will show the location of the
config file that is being used, if any.

.. _distutils configuration file: https://docs.python.org/3/distutils/configfile.html


Sphinx
======

To enable Sphinx

.. code:: shell

    $ pip install rstcheck[sphinx]

    # or

    $ pip install sphinx

With version 4.0 ``rstcheck`` added Sphinx as an optional extra where the version's lower
constraint is >=4.0 because of Sphinx's open upper constraints on jinja2 and markupsafe,
which result in import errors if not pinned below version 3 and 2 respectively. This happend
in Sphinx version 4.0.

You can also add Sphinx by yourself but the installed Sphinx version must be at least 2.0.

To check that Sphinx support is enabled

.. code:: shell

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

.. code:: yaml

    -   repo: https://github.com/myint/rstcheck
        rev: ''  # Use the sha / tag you want to point at
        hooks:
        -   id: rstcheck


Use with Mega-Linter:
=====================

Just install `Mega-Linter <https://nvuillam.github.io/mega-linter/>`__ in your repository,
`rstcheck <https://nvuillam.github.io/mega-linter/descriptors/rst_rstcheck/>`__
is part of the 70 linters activated out of the box.


Development
===========

This project relies on `poetry`_ as its management tool for dependencies, building and venvs.
You do not need to have `poetry`_ installed globally, but it is recommended to.

For development venv creation run

.. code:: shell

    $ poetry install

    # or without global `poetry`

    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ pip install poetry

With global `poetry`_ you do not need to activate the venv. `poetry`_ will run
commands inside the venv if you call them like this

.. code:: shell

    $ poetry run COMMAND

.. _poetry: https://python-poetry.org/


Testing
-------

Unit tests are in ``tests/test_rstcheck.py``.
System tests are in ``tests/test_as_cli_tool.py``.

System tests are composed of example good/bad input. The test inputs are
contained in the ``examples`` directory. For basic tests, adding a test should
just be a matter of adding files to ``examples/good`` or ``examples/bad``.

To run all the tests you have three options

.. code:: shell

    # With global `poetry` or with active development venv:
    $ poetry run tox

    # With active development venv:
    $ tox

    # Without `poetry` and development venv:
    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ pip install tox
    $ tox


Known limitations / FAQ
=======================

There are inherent limitations to what ``rstcheck`` can and cannot do. The reason for this is that
``rstcheck`` itself does not parse the rst source but gives it to ``docutils`` and gets the errors
back. Therefore rstcheck in the sense of rst source is more an error accumulation tool. The same
goes for the source code in supported code blocks.


History
=======


(next version)
--------------

- Fix inability to ignore ``code``, ``code-block`` and ``sourcecode`` directives (#79)
- Fix ``code-block`` options recognition (#62)
- Add section with ``Known limitations / FAQ`` to the README (#97)


.. _beaking_changes_v6:

BREAKING CHANGES
~~~~~~~~~~~~~~~~

- Drop support for sphinx < 2.0
- Drop default values for directves and roles for sphinx (#65)
- CLI options now take precedence over config file options (#96)


5.0.0 (2022-04-17)
------------------

- Add examples/ to sdist
- Add ``Development`` section to README and update ``Testing`` section
- Add ``Mega-Linter`` section to README
- Add ``BREAKING CHANGES`` sections to changelog


.. _beaking_changes_v5:

BREAKING CHANGES
~~~~~~~~~~~~~~~~

- Rewrite test.bash script in pytest test cases adn run them on linux in CI
- Rewrite old test suite in pytest and AAA style


4.1.0 (2022-04-16)
------------------

- Fix shebangs and scripts to use ``python3`` instead of ``python`` (#78)
- Improve the gcc checker functions by removing restrictions and
  using environment variable flags (#88)
- Fix pool size on windows by setting max to 61 (#86)
- Update test.bash script and makefile with new file location


4.0.0 (2022-04-15)
------------------

- Add inline type annotations
- Add ``sphinx`` as extra
- Update build process and set up ``poetry``
- Add ``pre-commit`` and ``tox`` for automated testing, linting and formatting
- Move from travis to github actions
- Activate dependabot


.. _beaking_changes_v4:

BREAKING CHANGES
~~~~~~~~~~~~~~~~

- Drop support for python versions prior 3.7


3.5.0 (2022-04-14)
------------------

- Deprecate python versions prior 3.7


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
