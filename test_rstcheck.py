#!/usr/bin/env python

"""Test suite for rstcheck."""

from __future__ import unicode_literals

import unittest

import rstcheck


class Tests(unittest.TestCase):

    def test_check(self):
        self.assertEqual(
            6,
            list(rstcheck.check(
                """\
Test
====

.. code-block:: python

    print(
"""))[0][0])

    def test_check_with_extra_blank_lines(self):
        self.assertEqual(
            6,
            list(rstcheck.check(
                """\
Test
====

.. code-block:: python

    print(



"""))[0][0])


if __name__ == '__main__':
    unittest.main()
