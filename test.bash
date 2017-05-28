#!/bin/bash

# System tests.

set -eux

trap "echo -e '\x1b[01;31mFailed\x1b[0m'" ERR

for name in examples/good/*.rst
do
    ./rstcheck.py "$name"
done

for name in examples/bad/*.rst
do
    if ./rstcheck.py "$name"
    then
        exit 1
    fi
done

# Test multiple files.
./rstcheck.py examples/good/*.rst

./rstcheck.py \
    --ignore-directives=my-directive \
    --ignore-role=some-custom-thing \
    examples/custom/good_with_custom.rst

./rstcheck.py --ignore-language=cpp examples/bad/bad_cpp.rst

./rstcheck.py - < examples/good/simple.rst
./rstcheck.py examples/with_configuration/good.rst

# Test multiple mix of good/bad files.
if ./rstcheck.py examples/bad/bad_cpp.rst examples/good/good.rst
then
    exit 1
fi

# "-" should only be allowed to be checked alone.
if ./rstcheck.py - examples/good/good.rst
then
    exit 1
fi

./rstcheck.py --report=none examples/bad/bad_rst.rst

if ./rstcheck.py missing_file.rst
then
    exit 1
fi

if python -c 'import sys; sys.exit(0 if sys.version_info >= (3,) else 1)'
then
    python -m doctest -v README.rst rstcheck.py
    ./rstcheck.py README.rst
fi

echo -e '\x1b[01;32mOkay\x1b[0m'
