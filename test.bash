#!/bin/bash -eux

trap "echo -e '\x1b[01;31mFailed\x1b[0m'" ERR

readonly root_path="$PWD"

./rstcheck.py examples/good.rst
./rstcheck.py examples/unicode.rst
./rstcheck.py examples/unknown.rst
./rstcheck.py - < examples/good.rst

cd examples/with_configuration
# This error does not affect the exit status for some reason.
../../rstcheck.py good.rst 2>&1 | grep --count ERROR | grep 0
cd "$root_path"

if ./rstcheck.py examples/bad_cpp.rst
then
    exit 1
fi

if ./rstcheck.py - < examples/bad_cpp.rst
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

if ./rstcheck.py examples/bad_rst_in_rst.rst
then
    exit 1
fi

if ./rstcheck.py missing_file.rst
then
    exit 1
fi

echo -e '\x1b[01;32mOkay\x1b[0m'
