FAQ / Known limitations / Known issues
======================================

.. rstcheck: ignore-roles=issue

You may also take a look at the `same section for rstcheck-core`_.

Known limitations
-----------------

There are inherent limitations to what ``rstcheck`` can and cannot do. The reason for this is that
``rstcheck`` itself relies on external tools for parsing and error reporting.
The rst source e.g. is given to ``docutils`` which then parses it and returns the errors.
Therefore rstcheck is more like an error accumulation tool. The same goes for the source
code in supported code blocks.

.. note::

    **Windows support is not stable!**

    Reason: Tests are failing with wrong positives and wrong negatives out of unknown reasons.
    See issue :issue:`107`.


Known issues
------------

ImportError: cannot import name 'get_terminal_size' from 'click.termui'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Affected rstcheck version(s): All 6.0 releases**

This issue is caused by an incompatibility of the dependency ``typer`` in version ``0.4.0`` and its
subdependency ``click`` with version ``>=8.1.0``.
The issue was fixed in ``typer`` version ``0.4.1``.

If you encounter this issue you can either:

- update ``rstcheck`` to a non affected version.
- manually limit ``click``'s upper version-bound to ``<8.1`` if you need to rely on ``typer``
  ``<0.4.1``.
- manually limit ``typer``'s lower version-bound to ``>=0.4.1``.
- manually limit ``typer``'s upper version-bound to ``<0.4`` which results in ``typer`` version
  ``0.3.2`` and ``click`` version ``<7.2``.

See :issue:`138` for reference.

.. _same section for rstcheck-core: https://rstcheck-core.readthedocs.io/en/latest/faq/
