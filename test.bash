#!/bin/bash -ex

./rstcheck good.rst
./rstcheck bad_cpp.rst | grep Error
./rstcheck bad_python.rst | grep Error
