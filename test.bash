#!/bin/bash

# System tests.

set -eux

trap "echo -e '\x1b[01;31mFailed\x1b[0m'" ERR

for name in examples/good/*.rst
do
    ./rstcheck/__init__.py "$name"
done

for name in examples/bad/*.rst
do
    if ./rstcheck/__init__.py "$name"
    then
        exit 1
    fi
done

# Test multiple files.
./rstcheck/__init__.py examples/good/*.rst

./rstcheck/__init__.py \
    --ignore-directives=my-directive \
    --ignore-role=some-custom-thing \
    examples/custom/good_with_custom.rst

./rstcheck/__init__.py --ignore-language=cpp examples/bad/bad_cpp.rst

./rstcheck/__init__.py - < examples/good/good.rst

# Test multiple mix of good/bad files.
if ./rstcheck/__init__.py examples/bad/bad_cpp.rst examples/good/good.rst
then
    exit 1
fi

# "-" should only be allowed to be checked alone.
if ./rstcheck/__init__.py - examples/good/good.rst
then
    exit 1
fi

./rstcheck/__init__.py --report=none examples/bad/bad_rst.rst

if ./rstcheck/__init__.py missing_file.rst
then
    exit 1
fi

./rstcheck/__init__.py --recursive examples/good
if ./rstcheck/__init__.py --recursive examples/bad
then
    exit 1
fi

# Test ignore messages
./rstcheck/__init__.py examples/bad/bad_rst.rst --ignore-messages '(Title .verline & underline mismatch\.$)'
if ./rstcheck/__init__.py examples/bad/bad_rst.rst --ignore-messages '(No match\.$)'
then
    exit 1
fi

# Test configuration file
./rstcheck/__init__.py examples/with_configuration/good.rst
if ./rstcheck/__init__.py examples/with_configuration/bad.rst
then
    exit 1
fi

# Ignore message on configuration file
./rstcheck/__init__.py examples/with_configuration/bad-2.rst

# Ignore existing configuration file
# It's doesn't matter if /dev/null is empty or doesn't exist
if ./rstcheck/__init__.py --config=/dev/null examples/with_configuration/good.rst
then
    exit 1
fi

# Check that we can use an unrelated configuration file
if ./rstcheck/__init__.py examples/without_configuration/good.rst
then
    # the check should fail if we don't have a configuration
    exit 1
fi
# specify the folder of the config file
./rstcheck/__init__.py --debug --config examples/with_configuration examples/without_configuration/good.rst
# specify an explicit config file
./rstcheck/__init__.py --debug --config examples/with_configuration/rstcheck.ini examples/without_configuration/good.rst
# specify a folder from which we have to walk up
./rstcheck/__init__.py --debug --config examples/with_configuration/dummydir examples/without_configuration/good.rst


python3 -m doctest -v README.rst rstcheck/__init__.py
./rstcheck/__init__.py README.rst

echo -e '\x1b[01;32mOkay\x1b[0m'
