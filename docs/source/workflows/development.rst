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

- ``poetry`` for dependency management, package metadata, building and publishing.
- ``tox`` for automated and isolated testing.
- ``pre-commit`` for automated QA checks via different linters and formatters.


Set up Local Development Environment
------------------------------------

The setup of a local development environment is pretty easy. The only tool you need is the
`poetry`_. You can install it via the `recommended way`_, which installs it globally on your
system or you can install it via ``pip`` in a self-created virtualenv (`virtualenv manual`_).

With ``poetry`` set up and ready we can create our development environment in just one
step::

    $ poetry install

This will install ``rstcheck`` along its main and development dependencies.


Working with the Local Development Environment
----------------------------------------------

Dependency management and more with poetry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

is used for dependency management, building and publishing ``rstcheck``.


Testing with tox
~~~~~~~~~~~~~~~~

To run all available tests and check simply run::

    $ tox

This will run:

- formatters and linters via ``pre-commit``.
- the full test suite with ``pytest``.
- a test coverage report.
- tests for the documentation.

Different environment lists are available and can be selected with ``tox -n <ENVLIST>``:

- test: run full test suite with ``pytest`` and report coverage.
- py3.7 - py3.10 run full test suite with specific python version and report coverage.
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
- ``pre-commit-install``: For installing pre-commit hooks as git hooks, to automatically run
  them before every commit.


IDE integration
~~~~~~~~~~~~~~~

The development environment has ``flakeheaven`` (a ``flake8`` wrapper), ``pylint`` and ``mypy``
installed to allow IDEs to use them for inline error messages. Their config is in
``pyproject.toml``. To run them actively use ``pre-commit`` and/or ``tox``.

.. highlight:: default


.. _Semantic Versioning: https://semver.org/
.. _poetry: https://python-poetry.org/docs/
.. _recommended way: https://python-poetry.org/docs/#installation
.. _virtualenv manual: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/
