#!/bin/bash -ex

./rstcheck.py --strict good.rst
./rstcheck.py --strict bad_cpp.rst | grep Error > /dev/null
./rstcheck.py --strict bad_python.rst | grep Error > /dev/null

echo -e '\x1b[01;32mOkay\x1b[0m'
