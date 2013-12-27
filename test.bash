#!/bin/bash -ex

./rstcheck.py good.rst
./rstcheck.py unknown.rst 2>&1 \
    | grep 'Unknown' > /dev/null
! ./rstcheck.py bad_cpp.rst
! ./rstcheck.py bad_python.rst

echo -e '\x1b[01;32mOkay\x1b[0m'
