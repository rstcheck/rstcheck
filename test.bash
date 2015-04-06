#!/bin/bash -eux

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
