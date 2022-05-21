Library
=======

Documentation for the open API of the library can be found in the :ref:`api:API` section.


Entry Points
------------

This library has two main entry points you can use:

:py:class:`rstcheck.runner.RstcheckMainRunner` class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``RstcheckMainRunner`` class the is main entry point. It manages the configuration state,
runs the check on the files, caches the found linting issues and prints them.


:py:func:`rstcheck.checker.check_file` function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``check_file`` function is a step deeper. It checks a single file and returns a list of
the found linting issues. This would be the entry point if you don't need the additional
management capabilities of the ``RstcheckMainRunner`` class.


Logging
-------

``rstcheck`` uses the standard library's ``logging`` module for its logging functionality.

Each python module has its own logger named after the ``__file__`` variable's value.

Following the `Official HOWTO`_ logging is deactivated by default, but can be activated,
if you as a developer provide a logging configuration.


.. _Official HOWTO: https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library__
