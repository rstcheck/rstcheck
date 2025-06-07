.. highlight:: console

Installation
============

This part of the documentation covers how to install the package.
It is recommended to install the package in a virtual environment.


Create virtual environment
--------------------------

There are several packages/modules for creating python virtual environments.
Here is a manual_ by the PyPA.


Installation from PyPI
----------------------

You can simply install the package from PyPI::

    $ pip install rstcheck


Extras
~~~~~~

``rstcheck`` has extras which can be installed to activate optional functionality:

- ``sphinx`` - To activate support for rst documents using the sphinx builder.
- ``toml`` - To activate support for TOML files as configuration files.

To install an extra simply add it in brackets like so::

    $ pip install rstcheck[sphinx,toml]


Pre-commit Hook with Extras
---------------------------

To use ``rstcheck`` in a Git pre-commit hook with optional features:

1. Install pre-commit::

     pip install pre-commit

2. Add to ``.pre-commit-config.yaml``::

     - repo: https://github.com/rstcheck/rstcheck
       rev: main # should be replaced with the current verison
       hooks:
         - id: rstcheck
           additional_dependencies: ['rstcheck[sphinx,toml]']

3. Run ``pre-commit install`` to activate.


Installation from source
------------------------

You can install ``rstcheck`` directly from a Git repository clone.
This can be done either by cloning the repository and installing from the local clone::

    $ git clone https://github.com/rstcheck/rstcheck.git
    $ cd rstcheck
    $ pip install .


Or installing directly via git::

    $ pip install git+https://github.com/rstcheck/rstcheck


You can also download the current version as `tar.gz` or `zip` file, extract it and
install it with pip like above.

.. highlight:: default


.. _manual: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/
