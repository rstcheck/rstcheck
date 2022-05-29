.. highlight:: console

Migration-Guides
================

Only breaking changes are mentioned here. New features or fixes are only mentioned if they
somehow correspond to a breaking change.


.. contents::


Version 5 to 6
--------------

With version 6 the whole code base was restructured. The core library was moved into its own
repository at ``rstcheck/rstcheck-core``.

``rstcheck`` moved from ``myint/rstcheck`` to ``rstcheck/rstcheck`` so you may want to update
links you have pointing to the old repository's location.

The ``master`` branch was renamed to ``main``. If you use git dependencies you may need to update
your reference.

The new logging system may help you find issues while migrating to v6.
You may then want to turn it on on the lowest level ``--log-level DEBUG``.


Configuration file
~~~~~~~~~~~~~~~~~~

- CLI options now overwrite settings in configuration files. Update your setup accordingly.

- The following configuration keys changed:

  - ``report`` renamed to ``report_level``
  - ``ignore_language`` renamed to ``ignore_languages``

- Set the ``--warn-unknown-settings`` CLI flag for warnings on unknown settings in
  configuration files.

- Numbers are no longer supported for ``report_level`` (old: ``report``)


CLI
~~~

- CLI options now overwrite settings in configuration files. Update your setup accordingly.

- Non existing files are ignored, but a warning is logged and the exit code is non-zero.

-The following CLI options changed:

  - ``--report`` renamed to ``--report-level`` and no longer accepts integers
  - ``--ignore-language`` renamed to ``--ignore-languages``
  - ``--ignore`` dropped -> use ``--ignore-languages``
  - ``--debug`` replaced with new ``--log-level`` -> use ``--log-level DEBUG`` for verbose output

- Numbers are no longer supported for ``--report-level`` (old: ``--report``)

- A non-existing path passed with ``--config`` results in a non-zero exit code.


Sphinx features
~~~~~~~~~~~~~~~

Support for sphinx prior version 2.0 was dropped.

Hard-coded default values for roles and directives coming from ``sphinx`` were dropped.
If you encounter a lot of unknown roles and directives this may be the reason
(`Example issue`_).

To fix this simply add sphinx to the environment from where you run ``rstcheck``::

   $ pip install sphinx  # directly

   $ pip install rstcheck[sphinx]  # or via extra

To check if sphinx support is activate run::

   $ rstcheck --help | grep Sphinx


Version 4 to 5
--------------

Nothing to do if you don't need the test suit of ``rstcheck``.

Use ``tox`` to run test suite.


Version 3 to 4
--------------

Use python 3.7 or newer to run ``rstcheck``.

.. highlight:: default


.. _Example issue: https://github.com/rstcheck/rstcheck/issues/109
