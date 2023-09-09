.. highlight:: console

Development
===========

``rstcheck`` uses `Semantic Versioning`_.

``rstcheck`` uses ``main`` as its single development branch. Therefore releases are
made from this branch. Only the current release is supported and bugfixes are released
with a patch release for the current minor release.


Tooling
-------

For development the following tools are used:

- ``setuptools`` for package metadata and building.
- ``twine`` for publishing.
- ``tox`` for automated and isolated testing.
- ``pre-commit`` for automated QA checks via different linters and formatters.


Set up Local Development Environment
------------------------------------

Simply create a virtualenv and run ``pip install -e .[dev]``. This will install
``rstcheck`` along its main and development dependencies.


Working with the Local Development Environment
----------------------------------------------

Dependency management
~~~~~~~~~~~~~~~~~~~~~

Dependencies are listed in ``pyproject.toml`` and are manually managed.


Testing with tox
~~~~~~~~~~~~~~~~

To run all available tests and check simply run::

    $ tox

This will run:

- formatters and linters via ``pre-commit``.
- the full test suite with ``pytest``.
- a test coverage report.
- tests for the documentation.

Different environment lists are available and can be selected with ``tox -m <ENVLIST>``:

- test: run full test suite with ``pytest`` and report coverage.
- py`X`.`Y` run full test suite with specific python version and report coverage.
- docs: run all documentation tests.


Linting and formatting pre-commit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

can be used directly from within the development environment or you can use
``tox`` to run it pre-configured.

There are 3 available ``tox`` envs with all use the same virtualenv:

- ``pre-commit``:
  For running any ``pre-commit`` command like ``tox -e pre-commit -- autoupdate --freeze``.
- ``pre-commit-run``:
  For running all hooks against the code base.
  A single hook's id can be passed as argument to run this hook only like
  ``tox -e pre-commit-run -- black``.


IDE integration
~~~~~~~~~~~~~~~

The development environment has ``flakeheaven`` (a ``flake8`` wrapper), ``pylint`` and ``mypy``
installed to allow IDEs to use them for inline error messages. Their config is in
``pyproject.toml``. To run them actively use ``pre-commit`` and/or ``tox``.

.. highlight:: default


.. _Semantic Versioning: https://semver.org/
