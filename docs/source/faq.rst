FAQ / Known limitations
=======================

There are inherent limitations to what ``rstcheck`` can and cannot do. The reason for this is that
``rstcheck`` itself relies on external tools for parsing and error reporting.
The rst source e.g. is given to ``docutils`` which then parses it and returns the errors.
Therefore rstcheck is more like an error accumulation tool. The same goes for the source
code in supported code blocks.

.. note::

    **Windows support is not stable!**

    Reason: Tests are failing with wrong positives and wrong negatives out of unknown reasons.
    See issue :issue:`107`.


.. rstcheck: ignore-roles=issue
