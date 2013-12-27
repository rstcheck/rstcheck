#!/bin/bash -ex

./rstcheck.py --strict-rst --strict-warnings good.rst
./rstcheck.py --strict-rst --strict-warnings unknown.rst 2>&1 \
    | grep 'Unknown' > /dev/null
! ./rstcheck.py --strict-rst --strict-warnings bad_cpp.rst
! ./rstcheck.py --strict-rst --strict-warnings bad_python.rst

echo -e '\x1b[01;32mOkay\x1b[0m'
