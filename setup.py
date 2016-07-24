#!/usr/bin/env python

"""Installer for rstcheck."""

import ast
import io

import setuptools


def version():
    """Return version string."""
    with io.open('rstcheck.py', encoding='utf-8') as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                return ast.parse(line).body[0].value.s


with io.open('README.rst', encoding='utf-8') as readme:
    setuptools.setup(
        name='rstcheck',
        version=version(),
        url='https://github.com/myint/rstcheck',
        description='Checks syntax of reStructuredText and code blocks nested '
                    'within it',
        long_description=readme.read(),
        classifiers=[
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Topic :: Software Development :: Quality Assurance',
        ],
        keywords='restructuredtext,lint,check,pypi,readme,rst,analyze',
        py_modules=['rstcheck'],
        entry_points={'console_scripts': ['rstcheck = rstcheck:main']},
        install_requires=['docutils', 'sphinx>=1.3']
    )
