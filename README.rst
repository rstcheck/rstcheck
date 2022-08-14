========
rstcheck
========

+-------------------+---------------------------------------------------------------------------------------------+
| **General**       | |maintenance_y| |license| |semver|                                                          |
|                   +---------------------------------------------------------------------------------------------+
|                   | |rtd|                                                                                       |
+-------------------+---------------------------------------------------------------------------------------------+
| **CI**            | |gha_tests| |gha_docu| |gha_qa| |pre_commit_ci|                                             |
+-------------------+---------------------------------------------------------------------------------------------+
| **PyPI**          | |pypi_release| |pypi_py_versions| |pypi_implementations|                                    |
|                   +---------------------------------------------------------------------------------------------+
|                   | |pypi_format| |pypi_downloads|                                                              |
+-------------------+---------------------------------------------------------------------------------------------+
| **Github**        | |gh_tag| |gh_last_commit|                                                                   |
|                   +---------------------------------------------------------------------------------------------+
|                   | |gh_stars| |gh_forks| |gh_contributors| |gh_watchers|                                       |
+-------------------+---------------------------------------------------------------------------------------------+


Checks syntax of reStructuredText and code blocks nested within it.

See the full documentation at `read-the-docs`_


.. contents::


Installation
============

From pip

.. code:: shell

    $ pip install rstcheck

To use pyproject.toml for configuration::

    $ pip install rstcheck[toml]

To add sphinx support::

    $ pip install rstcheck[sphinx]


Supported languages in code blocks
==================================

- Bash
- Doctest
- C (C99)
- C++ (C++11)
- JSON
- XML
- Python
- reStructuredText


Examples
========

.. rstcheck: ignore-languages=cpp,python,rst

With bad Python syntax:

.. code:: rst

    ====
    Test
    ====

    .. code:: python

        print(

.. code:: text

    $ rstcheck bad_python.rst
    bad_python.rst:7: (ERROR/3) (python) unexpected EOF while parsing

With bad C++ syntax:

.. code:: rst

    ====
    Test
    ====

    .. code:: cpp

        int main()
        {
            return x;
        }

.. code:: text

    $ rstcheck bad_cpp.rst
    bad_cpp.rst:9: (ERROR/3) (cpp) error: 'x' was not declared in this scope

With bad syntax in the reStructuredText document itself:

.. code:: rst

    ====
    Test
    ===

.. code:: text

    $ rstcheck bad_rst.rst
    bad_rst.rst:1: (SEVERE/4) Title overline & underline mismatch.


.. _read-the-docs: https://rstcheck.readthedocs.io


.. General

.. |maintenance_n| image:: https://img.shields.io/badge/Maintenance%20Intended-✖-red.svg?style=flat-square
    :target: http://unmaintained.tech/
    :alt: Maintenance - not intended

.. |maintenance_y| image:: https://img.shields.io/badge/Maintenance%20Intended-✔-green.svg?style=flat-square
    :target: http://unmaintained.tech/
    :alt: Maintenance - intended

.. |license| image:: https://img.shields.io/github/license/rstcheck/rstcheck.svg?style=flat-square&label=License
    :target: https://github.com/rstcheck/rstcheck/blob/main/LICENSE
    :alt: License

.. |semver| image:: https://img.shields.io/badge/Semantic%20Versioning-2.0.0-brightgreen.svg?style=flat-square
    :target: https://semver.org/
    :alt: Semantic Versioning - 2.0.0

.. |rtd| image:: https://img.shields.io/readthedocs/rstcheck/latest.svg?style=flat-square&logo=read-the-docs&logoColor=white&label=Read%20the%20Docs
    :target: https://rstcheck.readthedocs.io/en/latest/
    :alt: Read the Docs - Build Status (latest)


.. CI


.. |gha_tests| image:: https://img.shields.io/github/workflow/status/rstcheck/rstcheck/Test%20code/main?style=flat-square&logo=github&label=Test%20code
    :target: https://github.com/rstcheck/rstcheck/actions/workflows/test.yaml
    :alt: Test status

.. |gha_docu| image:: https://img.shields.io/github/workflow/status/rstcheck/rstcheck/Test%20documentation/main?style=flat-square&logo=github&label=Test%20documentation
    :target: https://github.com/rstcheck/rstcheck/actions/workflows/documentation.yaml
    :alt: Documentation status

.. |gha_qa| image:: https://img.shields.io/github/workflow/status/rstcheck/rstcheck/QA/main?style=flat-square&logo=github&label=QA
    :target: https://github.com/rstcheck/rstcheck/actions/workflows/qa.yaml
    :alt: QA status

.. |pre_commit_ci| image:: https://results.pre-commit.ci/badge/github/rstcheck/rstcheck/main.svg
    :target: https://results.pre-commit.ci/latest/github/rstcheck/rstcheck/main
    :alt: pre-commit status


.. PyPI

.. |pypi_release| image:: https://img.shields.io/pypi/v/rstcheck.svg?style=flat-square&logo=pypi&logoColor=FBE072
    :target: https://pypi.org/project/rstcheck/
    :alt: PyPI - Package latest release

.. |pypi_py_versions| image:: https://img.shields.io/pypi/pyversions/rstcheck.svg?style=flat-square&logo=python&logoColor=FBE072
    :target: https://pypi.org/project/rstcheck/
    :alt: PyPI - Supported Python Versions

.. |pypi_implementations| image:: https://img.shields.io/pypi/implementation/rstcheck.svg?style=flat-square&logo=python&logoColor=FBE072
    :target: https://pypi.org/project/rstcheck/
    :alt: PyPI - Supported Implementations

.. |pypi_format| image:: https://img.shields.io/pypi/format/rstcheck.svg?style=flat-square&logo=pypi&logoColor=FBE072
    :target: https://pypi.org/project/rstcheck/
    :alt: PyPI - Format

.. |pypi_downloads| image:: https://img.shields.io/pypi/dm/rstcheck.svg?style=flat-square&logo=pypi&logoColor=FBE072
    :target: https://pypi.org/project/rstcheck/
    :alt: PyPI - Monthly downloads



.. GitHub

.. |gh_tag| image:: https://img.shields.io/github/v/tag/rstcheck/rstcheck.svg?sort=semver&style=flat-square&logo=github
    :target: https://github.com/rstcheck/rstcheck/tags
    :alt: Github - Latest Release

.. |gh_last_commit| image:: https://img.shields.io/github/last-commit/rstcheck/rstcheck.svg?style=flat-square&logo=github
    :target: https://github.com/rstcheck/rstcheck/commits/main
    :alt: GitHub - Last Commit

.. |gh_stars| image:: https://img.shields.io/github/stars/rstcheck/rstcheck.svg?style=flat-square&logo=github
    :target: https://github.com/rstcheck/rstcheck/stargazers
    :alt: Github - Stars

.. |gh_forks| image:: https://img.shields.io/github/forks/rstcheck/rstcheck.svg?style=flat-square&logo=github
    :target: https://github.com/rstcheck/rstcheck/network/members
    :alt: Github - Forks

.. |gh_contributors| image:: https://img.shields.io/github/contributors/rstcheck/rstcheck.svg?style=flat-square&logo=github
    :target: https://github.com/rstcheck/rstcheck/graphs/contributors
    :alt: Github - Contributors

.. |gh_watchers| image:: https://img.shields.io/github/watchers/rstcheck/rstcheck.svg?style=flat-square&logo=github
    :target: https://github.com/rstcheck/rstcheck/watchers/
    :alt: Github - Watchers
