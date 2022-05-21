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


Installation from source
------------------------

You can install ``rstcheck`` directly from a Git repository clone.
This can be done either by cloning the repository and installing from the local clone::

    $ git clone https://github.com/Cielquan/rstcheck.git
    $ cd rstcheck
    $ pip install .


Or installing directly via git::

    $ pip install git+https://github.com/myint/rstcheck


You can also download the current version as `tar.gz` or `zip` file, extract it and
install it with pip like above.

.. highlight:: default


.. _manual: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/
