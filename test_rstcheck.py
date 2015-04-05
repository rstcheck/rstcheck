#!/usr/bin/env python

"""Test suite for rstcheck."""

from __future__ import unicode_literals

import unittest

import rstcheck


class Tests(unittest.TestCase):

    def assert_lines_equal(self, line_numbers, results):
        self.assertEqual(set(line_numbers), set(dict(results)))

    def test_parse_gcc_style_error_message(self):
        self.assertEqual(
            (32, 'error message'),
            rstcheck.parse_gcc_style_error_message(
                'filename:32:7: error message',
                filename='filename'))

    def test_parse_gcc_style_error_message_with_no_column(self):
        self.assertEqual(
            (32, 'error message'),
            rstcheck.parse_gcc_style_error_message(
                'filename:32: error message',
                filename='filename',
                has_column=False))

    def test_parse_gcc_style_error_message_with_parsing_error(self):
        with self.assertRaises(ValueError):
            rstcheck.parse_gcc_style_error_message(
                ':32:3 error message',
                filename='filename')

        with self.assertRaises(IndexError):
            rstcheck.parse_gcc_style_error_message(
                'filename:32: error message',
                filename='filename',
                has_column=True)

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

    def test_check_json_with_ignore(self):
        self.assert_lines_equal(
            [],
            rstcheck.check(
                """\
Test
====

.. code-block:: json

    {
        'abc': 123
    }

.. rstcheck: ignore-language=json,python,rst
"""))

    def test_check_json_with_unmatched_ignores_only(self):
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

.. rstcheck: ignore-language=cpp,python,rst
"""))

    def test_check_json_with_bad_ignore(self):
        self.assert_lines_equal(
            [7, 10],
            rstcheck.check(
                """\
Test
====

.. code-block:: json

    {
        'abc': 123
    }

.. rstcheck: ignore-language json,python,rst
"""))

    def test_check_with_extra_blank_lines_before(self):
        self.assert_lines_equal(
            [8],
            rstcheck.check(
                """\
Test
====

.. code-block:: python



    print(
"""))

    def test_check_with_extra_blank_lines_after(self):
        self.assert_lines_equal(
            [6],
            rstcheck.check(
                """\
Test
====

.. code-block:: python

    print(



"""))

    def test_check_with_extra_blank_lines_before_and_after(self):
        self.assert_lines_equal(
            [8],
            rstcheck.check(
                """\
Test
====

.. code-block:: python



    print(



"""))

    def test_check_rst(self):
        self.assert_lines_equal(
            [2],
            rstcheck.check(
                """\
Test
===
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

    def test_ignore_sphinx_directives(self):
        self.assert_lines_equal(
            [],
            rstcheck.check(
                """\
.. toctree::
    :maxdepth: 2

    intro
    strings
    datatypes
    numeric
    (many more documents listed here)

.. highlight:: python
   :linenothreshold: 5

::

   print('Hello')

.. code-block:: ruby
   :linenos:

   puts "Hello!"

.. code-block:: python
   :linenos:
   :emphasize-lines: 3,5

   def some_function():
       interesting = False
       print('This line is highlighted.')
       print('This one is not...')
       print('...but this one is.')

.. literalinclude:: rstcheck.py
   :language: python
   :linenos:

"""))

    def test_check_doctest(self):
        self.assert_lines_equal(
            [5],
            rstcheck.check(
                """\
Testing
=======

>>> x = 1
>>>> x
1
"""))

    def test_check_doctest_with_ignore(self):
        self.assert_lines_equal(
            [],
            rstcheck.check(
                """\
Testing
=======

>>> x = 1
>>>> x
1

.. rstcheck: ignore-language=doctest
"""))

    def test_check_doctest_in_code_block(self):
        self.assert_lines_equal(
            [7],
            rstcheck.check(
                """\
Testing
=======

.. code-block:: doctest

    >>> x = 1
    >>>> x
    1
"""))

    def test_check_doctest_in_python_code_block(self):
        """I'm not sure if this is correct, but I've seen people do it."""
        self.assert_lines_equal(
            [7],
            rstcheck.check(
                """\
Testing
=======

.. code-block:: python

    >>> x = 1
    >>>> x
    1
"""))


if __name__ == '__main__':
    unittest.main()
