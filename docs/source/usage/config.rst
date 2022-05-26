Configuration
=============

.. contents::

``rstcheck``'s config system knows three sources:

- Inline comments (*for config and flow control instructions*)
- CLI options
- Config files (*INI and TOML*)


Order of application
--------------------

The config sources apply according to a set of rules:

#. *Flow control instructions* from inline comments:

   - **always apply** regardless of other config.
   - are **expressive** and say for themselves what they apply to.

#. Config from inline comments:

   - **always apply** regardless of other config.
   - **always apply for the whole file** regardless where they are placed.
   - is **added** to the remaining config and does **not overwrite** it.

#. CLI options **always overwrite** config comming from a file.
#. File config has the lowest priority.


Configuration sources
---------------------

Now let's take a deeper look at the different sources of config.


Inline comments
~~~~~~~~~~~~~~~

Inline comments are simply rst comments starting with ``rstcheck:``.
There are two types of inline comments:

- Simple inline config e.g. ``ignore-languages=python`` which follows the syntax of ``key=value``.
- Flow control instructions e.g. ``ignore-next-code-block`` which follows the syntax of
  ``words-divided-by-dashes``.

Here is an example with both of them:

.. code-block:: rst

    Example
    =======

    .. rstcheck: ignore-next-code-block
    .. code-block:: python

        print("Hello World")

    .. rstcheck: ignore-languages=python


CLI options
~~~~~~~~~~~

For information on the CLI options please see the :ref:`usage/cli:CLI` section.


Configuration files
~~~~~~~~~~~~~~~~~~~

``rstcheck`` has an automatic config file detection mechanic. This mechanic includes
the following config files sorted by priority:

#. .rstcheck.cfg
#. pyproject.toml
#. setup.cfg

When a directory is searched for a config file, the first found config section is
taken and the search is not aborted on the first file found.
This means that if you for example have a pyproject.toml file without a matching config
section and an setup.cfg file with a matching section, the section from setup.cfg would be used.
pyproject.toml would be searched first, but nothing would be found and so the search would continue.

For each rst source file that is linted, its parent directory is searched for a config file.
If the parent directory has no config file with a matching config section the parent's
parent directory is searched next. This continues up the directory tree until the root directory.
If no config file is found, the default values for each setting apply.

This whole mechanic is deactivated, when a config file or directory is explicity set.
See the `Configuration file`_ section for more information on setting a config file/directory.

``rstcheck`` supports two types of config formats: **INI** and **TOML**.
They are written pretty similar, but have some differences.
The two following sections explain both formats.

Files ending on ``.toml`` are parsed as TOML files.
Every other file is parsed as an INI file.

If ``.rstcheck.cfg`` does not contain a valid section a warning is printed.


INI format
^^^^^^^^^^

In INI format all config related to ``rstcheck`` must go into a ``[rstcheck]`` section.

The default INI format applies: ``key = value``.
Lists are comma-separated strings, which can be multiline.
Whitespace before and after a key or value is ignored.
Trailing commas are optional.

Here is an example:

.. code-block:: ini

    [rstcheck]
    report_level=WARNING
    ignore_directives =
        one,
        two,
        three,
    ignore_roles=src, RFC
    ignore_substitutions=
        image_link
    ignore_languages=
        python,
        cpp
    ignore_messages=(Document or section may not begin with a transition\.$)


TOML format
^^^^^^^^^^^

.. note::

    TOML format is only supported when the python library ``tomli`` is importable.
    See the :ref:`installation:Installation` section for more information.

In TOML format all config related to ``rstcheck`` must go into the ``[tool.rstcheck]``
dictionary. This is due to the python convention for the ``pyproject.toml`` file, which
``rstcheck`` uses for all TOML files.

The official TOML syntax applies here, so strings are strings and lists are lists for exmaple.

Here is an example:

.. code-block:: toml

    [tool.rstcheck]
    report_level = "WARNING"
    ignore_directives = [
        "one",
        "two",
        "three",
    ]
    ignore_roles = ["src", "RFC"]
    ignore_substitutions = [
        "image_link"
    ]
    ignore_languages = [
        "python",
        "cpp"
    ]
    ignore_messages = "(Document or section may not begin with a transition\.$)"


Configuration options
---------------------

Now it's time for all the available settings you can set.


Configuration file
~~~~~~~~~~~~~~~~~~

Supported sources:

- CLI (``--config PATH`` )

With the ``--config`` CLI option you can set a config file or directory.
The path may be relative or absolute.

If the passed path does not exist the runner exits with an error, which is logged.

If the path is a literal ``NONE``, no file is loaded or directory serached, this includes
the automatic config file detection mechanic.

When the path points to a file, this concrete file is read and searched for a matching
config section.
If no section is found a warning is logged and no file config is used.

When the path is a directory, this directory is search for a config file, like described
in the earlier `Configuration files`_ section, except that only this directry is saerch and
not the directry tree.


Recursive resolution
~~~~~~~~~~~~~~~~~~~~

Supported sources:

- CLI (``--recursive`` or ``-r``)

By default only files passed to the CLI runner are checked and directories are ignored.
When this config is set, passed directories are searched recursively for rst source files.


Report level
~~~~~~~~~~~~

Supported sources:

- CLI (``--report-level LEVEL``)
- File (key: ``report_level``, value: LEVEL)

The level at which linting issues should be printed. The following levels are supported:

- INFO (default)
- WARNING
- ERROR
- SEVERE
- NONE

This currently only applies to issues with rst source.
Issues in code blocks are on ERROR level and always printed,
even if the level is set to SEVERE or NONE.

The level can be set case insensitive.


Logging level
~~~~~~~~~~~~~

Supported sources:

- CLI (``--log-level LEVEL``)

The level at which additional information besides linting issues should be printed.
The following levels are supported:

- DEBUG
- INFO
- WARNING (default)
- ERROR
- CRITICAL

The level can be set case insensitive.


Ignore directives
~~~~~~~~~~~~~~~~~

Supported sources:

- Inline comments (key: ``ignore-directives``, value: list of directives)
- CLI (``--ignore-directives D1,D2,...``)
- File (key: ``ignore_directives``, value: list of directives)

A list of directives to ignore while checking rst source.


Ignore roles
~~~~~~~~~~~~

Supported sources:

- Inline comments (key: ``ignore-roles``, value: list of roles)
- CLI (``--ignore-roles R1,R2,...``)
- File (key: ``ignore_roles``, value: list of roles)

A list of roles to ignore while checking rst source.


Ignore substitutions
~~~~~~~~~~~~~~~~~~~~

Supported sources:

- Inline comments (key: ``ignore-substitutions``, value: list of substitutions)
- CLI (``--ignore-substitutions S1,S2,...``)
- File (key: ``ignore_substitutions``, value: list of substitutions)

A list of substitutions to ignore while checking rst source.


Ignore specific code-block languages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Supported sources:

- Inline comments (key: ``ignore-languages``, value: list of languages)
- CLI (``--ignore-languages L1,L2,...``)
- File (key: ``ignore_languages``, value: list of languages)

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


Ignore specific error messages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Supported sources:

- CLI (``--ignore-messages REGEX_STRING``)
- File (key: ``ignore_messages``, value: regular expression string)

A list of linting issue messages to ignore while checking rst source and code blocks.

.. note::

    In TOML format a list of strings is also valid. The list's entries will be
    concatenated with the OR operator "|" between each entry.


Control Flow instructions
-------------------------

There are also control flow instructions which are only available as inline comments.
They change the flow of checking the rst source, hence the name.


Skipping code blocks
~~~~~~~~~~~~~~~~~~~~

With the ``ignore-next-code-block`` flow control instruction you can skip single code blocks.
This way you don't have to use the heavy tools like ignoring a whole language or directive.

The instruction **must** be placed in the line directly above the code block directive like so:


.. code-block:: rst

    .. rstcheck: ignore-next-code-block
    .. code-block:: python

        print("Hello world")


Examples with explanation
-------------------------

These examples are cases to show concepts of configuration in ``rstcheck``.
They don't always follow best practices.


Only inline comments
~~~~~~~~~~~~~~~~~~~~

.. code-block:: rst

    Example
    =======

    .. rstcheck: ignore-next-code-block
    .. code-block:: python

        print("Here is an error."

    .. rstcheck: ignore-languages=python

In this example the code-block would be ignored/skipped due to the flow control instruction.
But the code-block's language is python which is on the ignore list for languages, because of the
config at the bottom. This means if you remove the flow control instruction, the
code-block would still be skipped and the error inside would ignored.
