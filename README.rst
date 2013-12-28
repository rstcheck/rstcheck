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

With bad Python syntax:

.. code-block:: rst

    ====
    Test
    ====

    .. code-block:: python

        print(

::

    $ rstcheck bad_python.rst
    bad_python.rst:5: (ERROR/3) unexpected EOF while parsing

With bad C++ syntax:

.. code-block:: rst

    ====
    Test
    ====

    .. code-block:: cpp

        #include <iostream>

        int main()
        {

::

    $ rstcheck bad_cpp.rst
    bad_cpp.rst:9: (ERROR/3)  error: expected '}' at end of input
