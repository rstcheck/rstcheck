========
rstcheck
========

Checks code blocks in ReStructuredText.


Installation
============

From pip::

    $ pip install --upgrade rstcheck

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
    Compiling '/var/folders/eD/eDkaCQuWHJG9f-G6kmkpgk+++TI/-Tmp-/tmpn874va.py'...
    Okay

With bad C++ syntax::

    $ rstcheck bad_cpp.rst
    + grep Error
    #include <iostream>

    int main()
    {
    /var/folders/eD/eDkaCQuWHJG9f-G6kmkpgk+++TI/-Tmp-/tmpeg1c35.cpp: In function 'int main()':
    /var/folders/eD/eDkaCQuWHJG9f-G6kmkpgk+++TI/-Tmp-/tmpeg1c35.cpp:4:1: error: expected '}' at end of input
     {
     ^
    Error

With bad Python syntax::

    $ rstcheck bad_python.rst
    print(
    SyntaxError: unexpected EOF while parsing
    Error
