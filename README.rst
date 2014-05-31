========
rstcheck
========

.. image:: https://travis-ci.org/myint/rstcheck.svg?branch=master
    :target: https://travis-ci.org/myint/rstcheck
    :alt: Build status

Checks code blocks in reStructuredText.

This is in addition to the usual docutils reStructuredText syntax check itself.


Installation
============

From pip::

    $ pip install --upgrade rstcheck


Supported languages in code blocks
==================================

- Bash
- C (C99)
- C++ (C++11)
- JSON
- Python
- reStructuredText


Example
=======

With bad Python syntax:

.. code-block:: rst

    ====
    Test
    ====

    .. code-block:: python

        print(

::

    $ rstcheck bad_python.rst
    bad_python.rst:7: (ERROR/3) (python) unexpected EOF while parsing

With bad C++ syntax:

.. code-block:: rst

    ====
    Test
    ====

    .. code-block:: cpp

        int main()
        {
            return x;
        }

::

    $ rstcheck bad_cpp.rst
    bad_cpp.rst:9: (ERROR/3) (cpp) error: 'x' was not declared in this scope

With bad syntax in the reStructuredText document itself:

.. code-block:: rst

    ====
    Test
    ===

::

    $ rstcheck bad_rst.rst
    bad_rst.rst:1: (SEVERE/4) Title overline & underline mismatch.
