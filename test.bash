#!/bin/bash -eux

./rstcheck.py examples/good.rst
./rstcheck.py examples/unknown.rst

if ./rstcheck.py examples/bad_cpp.rst
then
    exit 1
fi

if ./rstcheck.py examples/bad_python.rst
then
    exit 1
fi

if ./rstcheck.py examples/bad_rst.rst
then
    exit 1
fi

echo -e '\x1b[01;32mOkay\x1b[0m'
