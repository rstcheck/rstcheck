#!/usr/bin/env python

"""Test suite for rstcheck."""

from __future__ import unicode_literals

import unittest

import rstcheck


class Tests(unittest.TestCase):

    def assert_lines_equal(self, line_numbers, results):
        self.assertEqual(line_numbers,
                         list(dict(results).keys()))

    def test_check(self):
        self.assert_lines_equal(
            [6],
            rstcheck.check(
                """\
Test
====

.. code-block:: python

    print(
"""))

    def test_check_json(self):
        self.assert_lines_equal(
            [7],
            rstcheck.check(
                """\
Test
====

.. code-block:: json

    {
        'abc': 123
    }
"""))

    def test_check_with_extra_blank_lines(self):
        self.assert_lines_equal(
            [6],
            rstcheck.check(
                """\
Test
====

.. code-block:: python

    print(



"""))

    def test_check_nested_rst(self):
        self.assert_lines_equal(
            [32],
            rstcheck.check(
                """\
Test
====

.. code-block:: rst

    Test
    ====

    .. code-block:: rst


        Test
        ====

        .. code-block:: rst

            Test
            ====

            .. code-block:: rst

                Test
                ====

                .. code-block:: rst

                    Test
                    ====

                    .. code-block:: python

                        print(
"""))


if __name__ == '__main__':
    unittest.main()
