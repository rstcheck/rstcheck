#!/bin/bash

set -eux

trap "echo -e '\x1b[01;31mFailed\x1b[0m'" ERR

if python -c 'import sys; sys.exit(0 if sys.version_info >= (3,) else 1)'
then
    ./rstcheck.py examples/good.rst README.rst
    python -m doctest -v README.rst rstcheck.py
fi

./rstcheck.py examples/good.rst
./rstcheck.py examples/unicode.rst
./rstcheck.py examples/unknown.rst
./rstcheck.py - < examples/good.rst
./rstcheck.py examples/with_configuration/good.rst
./rstcheck.py examples/good_cpp_with_local_include.rst

./rstcheck.py \
    --ignore-directives=my-directive \
    --ignore-role=some-custom-thing \
    examples/good_with_custom.rst

# Test multiple files.
./rstcheck.py examples/good.rst examples/unicode.rst

if ./rstcheck.py examples/bad_cpp.rst
then
    exit 1
fi

./rstcheck.py --ignore-language=cpp examples/bad_cpp.rst

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

# Test multiple files.
if ./rstcheck.py examples/bad_cpp.rst examples/good.rst
then
    exit 1
fi

# "-" should only be allowed to be checked alone.
if ./rstcheck.py - examples/good.rst
then
    exit 1
fi

./rstcheck.py --report=none examples/bad_rst.rst

if ./rstcheck.py examples/bad_rst_in_rst.rst
then
    exit 1
fi

if ./rstcheck.py missing_file.rst
then
    exit 1
fi

echo -e '\x1b[01;32mOkay\x1b[0m'
