#!/bin/bash -eux

./rstcheck.py good.rst
./rstcheck.py unknown.rst

if ./rstcheck.py bad_cpp.rst
then
    exit 1
fi

if ./rstcheck.py bad_python.rst
then
    exit 1
fi

echo -e '\x1b[01;32mOkay\x1b[0m'
