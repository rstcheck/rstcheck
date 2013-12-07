========
rstcheck
========

Checks code blocks in ReStructuredText.


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

With good input::

    $ rstcheck good.rst
    #include <iostream>

    int main()
    {
    }
    Okay
    print(1)
    Okay

With bad C++ syntax::

    $ rstcheck bad_cpp.rst
    #include <iostream>

    int main()
    {
    tmpeg1c35.cpp: In function 'int main()':
    tmpeg1c35.cpp:4:1: error: expected '}' at end of input
     {
     ^
    Error

With bad Python syntax::

    $ rstcheck bad_python.rst
    print(
    SyntaxError: unexpected EOF while parsing
    Error

Strict mode
===========

To treat warnings as errors::

    $ rstcheck --strict-warnings input.rst

To check ReStructuredText syntax itself more thoroughly::

    $ rstcheck --strict-rst input.rst
