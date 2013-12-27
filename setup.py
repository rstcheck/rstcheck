#!/usr/bin/env python

"""Installer for rstcheck."""

import ast
import setuptools


def version():
    """Return version string."""
    with open('rstcheck.py') as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                return ast.parse(line).body[0].value.s


with open('README.rst') as readme:
    setuptools.setup(
        name='rstcheck',
        version=version(),
        url='http://github.com/myint/rstcheck',
        description='Checks code blocks in ReStructuredText.',
        long_description=readme.read(),
        classifiers=[
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3'
            'Topic :: Software Development :: Quality Assurance'],
        py_modules=['rstcheck'],
        entry_points={'console_scripts': ['rstcheck = rstcheck:main']},
        install_requires=['docutils']
    )
