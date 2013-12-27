========
rstcheck
========

.. image:: https://travis-ci.org/myint/rstcheck.png?branch=master
    :target: https://travis-ci.org/myint/rstcheck
    :alt: Build status

Checks code blocks in reStructuredText.


Installation
============

From pip::

    $ pip install --upgrade rstcheck

Supported languages in code blocks
==================================

- Bash
- C (C99)
- C++ (C++11)
- Python


Example
=======

With bad Python syntax::

    $ cat bad_python.rst
    ====
    Test
    ====

    .. code-block:: python

        print(

    $ rstcheck bad_python.rst
    bad_python.rst:5: (ERROR/3) unexpected EOF while parsing
