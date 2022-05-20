Configuration
=============

``rstcheck``'s configuration system knows three sources and they apply in the following order:

#. Inline configuration comments
#. CLI options
#. Configuration files

This means that e.g. a configuration via CLI overwrites configuration from a file.


Configuration options
---------------------


Configuration file
~~~~~~~~~~~~~~~~~~

A configuration file can only be set via the ``--config`` CLI option.
After the option you must specify a path. The path may be relativ or absolute.

When the path points to a file, this concrete file is read and searched for a configuration
section for ``rstcheck``. If no section is found a warning is printed and no file configuration
is used. If the file is not found an error is raised.

When the path is a directory, this directory is search for the following configuration files in this
order:

#. .rstcheck.cfg
#. pyproject.toml
#. setup.cfg

If one files does not exist or contain a configuration section for ``rstcheck`` the next is tried.
If ``.rstcheck.cfg`` does not contain a valid section a warning is printed.

INI style files are searched for a ``[rstcheck]`` section.

TOML files are searched for a ``[tool.rstcheck]`` section.

.. note::

    ``pyproject.toml`` and TOML files in general are only supported if ``tomli`` is importable.
    ``tomli`` can be installed via the ``toml`` extra. See the :ref:`installation:Installation`
    section for more information.

When ``--config`` is not set two things happen implicitly:

1. The current working directory is searched for one of the above configuration files,
   as if ``--config .`` was set.
2. The directory of each rst file which is checked is also searched for the above configuration
   files. These files may contain configuration specific to the files in this directory.
   If the file's directory does not contain a valid configuration file the parent directories
   are searched up the directory tree until the root.


Recursive resolution
~~~~~~~~~~~~~~~~~~~~

By default only files passed to the CLI application are checked and directories are ignored.
When this flag is set, passed directories are searched recursively for rst source files.

Can only be activated with the ``--recursive`` or ``-r`` CLI flag.


Report level
~~~~~~~~~~~~

The level at which linting issues should be printed. The following levels are supported:

- INFO (default)
- WARNING
- ERROR
- SEVERE
- NONE

This currently only applies to issues with rst source.
Issues in code blocks are on ERROR level and always printed,
even if the level is set to SEVERE or NONE.

Can be set via the CLI option ``--report-level`` or
in a configuration file with the ``report_level`` key.
The level can be set case insensitive.


Logging level
~~~~~~~~~~~~~

The level at which addtional information besides linting issues should be printed.
The following levels are supported:

- DEBUG
- INFO
- WARNING (default)
- ERROR
- CRITICAL

Can only be set via the ``--log-level`` CLI option.
The level can be set case insensitive.


Ignore directives
~~~~~~~~~~~~~~~~~

A list of directives to ignore while checking rst source.

Can be set via the CLI option ``--ignore-directives`` or
in a configuration file with the ``ignore_directives`` key.
On CLI and in INI format a comma separated list is expected.
In TOML format a list of strings is expected.


Ignore roles
~~~~~~~~~~~~

A list of roles to ignore while checking rst source.

Can be set via the CLI option ``--ignore-roles`` or
in a configuration file with the ``ignore_roles`` key.
On CLI and in INI format a comma separated list is expected.
In TOML format a list of strings is expected.


Ignore substitutions
~~~~~~~~~~~~~~~~~~~~

A list of substitutions to ignore while checking rst source.

Can be set via the CLI option ``--ignore-substitutions`` or
in a configuration file with the ``ignore_substitutions`` key.
On CLI and in INI format a comma separated list is expected.
In TOML format a list of strings is expected.


Ignore specific code-block languages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A list of languages to ignore for code blocks in rst source.
Unsupported languages are ignored automatically.

Supported languages are:

- Bash
- Doctest
- C (C99)
- C++ (C++11)
- JSON
- XML
- Python
- reStructuredText

Can be set via the CLI option ``--ignore-languages`` or
in a configuration file with the ``ignore_languages`` key
or as an inline configuration comment with the ``ignore-languages`` key.
On CLI, in INI format and as inline configuration comment a comma separated list is expected.
In TOML format a list of strings is expected.


Ignore specific error messages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A list of linting issue messages to ignore while checking rst source and code blocks.

Can be set via the CLI option ``--ignore-messages`` or
in a configuration file with the ``ignore_messages`` key.
On CLI and in INI format a regular expression string is expected.
In TOML format a single string or a list of strings is expected. The list's entries will be
concatenated and the OR operator "|" will be set between each entry.


Configuration Examples
----------------------

Inline configuration comment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Inline configuration is passed after a ``rstcheck:`` in a rst comment.

.. code-block:: rst

    Example
    =======

    .. code-block:: python

        print("Hello world")

    .. rstcheck: ignore-languages=python


INI Configuration file
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: ini

    [rstcheck]
    report_level=warning
    ignore_directives =
        one,
        two,
        three,
    ignore_roles=src,RFC
    ignore_substitutions=image_link
    ignore_languages=python,cpp
    ignore_messages=(Document or section may not begin with a transition\.$)


TOML Configuration file
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: toml

    [tool.rstcheck]
    report_level = "WARNING"
    ignore_directives = [
        "one",
        "two",
        "three",
    ]
    ignore_roles = ["src", "RFC"]
    ignore_substitutions = ["image_link"]
    ignore_languages = ["python", "cpp"]
    ignore_messages = "(Document or section may not begin with a transition\.$)"
