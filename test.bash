#!/bin/bash -ex

./rstcheck.py --strict good.rst
./rstcheck.py --strict bad_cpp.rst | grep Error > /dev/null
./rstcheck.py --strict bad_python.rst | grep Error > /dev/null
