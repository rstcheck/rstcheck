#!/bin/bash -ex

./rstcheck.py good.rst
./rstcheck.py bad_cpp.rst | grep Error
./rstcheck.py bad_python.rst | grep Error
