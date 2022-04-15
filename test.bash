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

./rstcheck.py - < examples/good/good.rst

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

./rstcheck.py --recursive examples/good
if ./rstcheck.py --recursive examples/bad
then
    exit 1
fi

# Test ignore messages
./rstcheck.py examples/bad/bad_rst.rst --ignore-messages '(Title .verline & underline mismatch\.$)'
if ./rstcheck.py examples/bad/bad_rst.rst --ignore-messages '(No match\.$)'
then
    exit 1
fi

# Test configuration file
./rstcheck.py examples/with_configuration/good.rst
if ./rstcheck.py examples/with_configuration/bad.rst
then
    exit 1
fi

# Ignore message on configuration file
./rstcheck.py examples/with_configuration/bad-2.rst

# Ignore existing configuration file
# It's doesn't matter if /dev/null is empty or doesn't exist
if ./rstcheck.py --config=/dev/null examples/with_configuration/good.rst
then
    exit 1
fi

# Check that we can use an unrelated configuration file
if ./rstcheck.py examples/without_configuration/good.rst
then
    # the check should fail if we don't have a configuration
    exit 1
fi
# specify the folder of the config file
./rstcheck.py --debug --config examples/with_configuration examples/without_configuration/good.rst
# specify an explicit config file
./rstcheck.py --debug --config examples/with_configuration/rstcheck.ini examples/without_configuration/good.rst
# specify a folder from which we have to walk up
./rstcheck.py --debug --config examples/with_configuration/dummydir examples/without_configuration/good.rst


python3 -m doctest -v README.rst rstcheck.py
./rstcheck.py README.rst

echo -e '\x1b[01;32mOkay\x1b[0m'
