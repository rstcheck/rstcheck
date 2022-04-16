#!/usr/bin/env python3

"""Test suite for rstcheck."""


import typing
import unittest

import rstcheck


# We don't do this in the module itself to avoid mutation.
rstcheck.ignore_sphinx()


class Tests(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """Test suite."""

    @staticmethod
    def assert_lines_equal(
        line_numbers: typing.List[int], results: rstcheck.YieldedErrorTuple
    ) -> None:
        """Test if the line numbers match the results."""
        assert set(line_numbers) == set(dict(results))

    @staticmethod
    def test_parse_gcc_style_error_message() -> None:
        """Test `parse_gcc_style_error_message`."""
        assert (32, "error message") == rstcheck.parse_gcc_style_error_message(
            "filename:32:7: error message", filename="filename"
        )

    @staticmethod
    def test_parse_gcc_style_error_message_with_no_column() -> None:
        """Test `parse_gcc_style_error_message` with no column."""
        assert (32, "error message") == rstcheck.parse_gcc_style_error_message(
            "filename:32: error message", filename="filename", has_column=False
        )

    def test_parse_gcc_style_error_message_with_parsing_error(self) -> None:
        """Test `parse_gcc_style_error_message` raising exceptions."""
        with self.assertRaises(ValueError):  # noqa: PT009
            rstcheck.parse_gcc_style_error_message(":32:3 error message", filename="filename")

        with self.assertRaises(IndexError):  # noqa: PT009
            rstcheck.parse_gcc_style_error_message(
                "filename:32: error message", filename="filename", has_column=True
            )

    def test_check(self) -> None:
        """Test `check`."""
        self.assert_lines_equal(
            [6],
            rstcheck.check(
                """\
Test
====

.. code:: python

    print(
"""
            ),
        )

    def test_check_code_block(self) -> None:
        """Test `check` with python code block."""
        self.assert_lines_equal(
            [6],
            rstcheck.check(
                """\
Test
====

.. code-block:: python

    print(
"""
            ),
        )

    def test_check_json(self) -> None:
        """Test `check` with json."""
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
"""
            ),
        )

    def test_check_json_with_ignore(self) -> None:
        """Test `check` with json and ignore."""
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
"""
            ),
        )

    def test_check_json_with_unmatched_ignores_only(self) -> None:
        """Test `check` with json and unmatched ignore."""
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
"""
            ),
        )

    def test_check_json_with_bad_ignore(self) -> None:
        """Test `check` with json and bad ignore."""
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
"""
            ),
        )

    def test_check_xml(self) -> None:
        """Test `check` with xml."""
        self.assert_lines_equal(
            [8],
            rstcheck.check(
                """\
Test
====

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <root>
       </abc>123<abc>
    </root>
"""
            ),
        )

    def test_check_xml_with_ignore(self) -> None:
        """Test `check` with xml and ignore."""
        self.assert_lines_equal(
            [],
            rstcheck.check(
                """\
Test
====

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <root>
       </abc>123<abc>
    </root>

.. rstcheck: ignore-language=xml,python,rst
"""
            ),
        )

    def test_check_xml_with_unmatched_ignores_only(self) -> None:
        """Test `check` with xml and unmatched ignore."""
        self.assert_lines_equal(
            [8],
            rstcheck.check(
                """\
Test
====

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <root>
       </abc>123<abc>
    </root>

.. rstcheck: ignore-language=cpp,python,rst
"""
            ),
        )

    def test_check_xml_with_bad_ignore(self) -> None:
        """Test `check` with xml and bad ignore."""
        self.assert_lines_equal(
            [8, 11],
            rstcheck.check(
                """\
Test
====

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <root>
       </abc>123<abc>
    </root>

.. rstcheck: ignore-language xml,python,rst
"""
            ),
        )

    def test_check_with_extra_blank_lines_before(self) -> None:
        """Test `check` with python and extra blank lines before."""
        self.assert_lines_equal(
            [8],
            rstcheck.check(
                """\
Test
====

.. code-block:: python



    print(
"""
            ),
        )

    def test_check_with_extra_blank_lines_after(self) -> None:
        """Test `check` with python and extra blank lines after."""
        self.assert_lines_equal(
            [6],
            rstcheck.check(
                """\
Test
====

.. code-block:: python

    print(



"""
            ),
        )

    def test_check_with_extra_blank_lines_before_and_after(self) -> None:
        """Test `check` with python and extra blank lines before and after."""
        self.assert_lines_equal(
            [8],
            rstcheck.check(
                """\
Test
====

.. code-block:: python



    print(



"""
            ),
        )

    def test_check_rst(self) -> None:
        """Test `check` with rst."""
        self.assert_lines_equal(
            [2],
            rstcheck.check(
                """\
Test
===
"""
            ),
        )

    def test_check_rst_report_level(self) -> None:
        """Test `check` with rst and set report level."""
        self.assert_lines_equal(
            [],
            rstcheck.check(
                """\
Test
===
""",
                report_level=5,
            ),
        )

    def test_check_nested_rst(self) -> None:
        """Test `check` with nested rst."""
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
"""
            ),
        )

    @unittest.skipIf(not rstcheck.SPHINX_INSTALLED, "Requires Sphinx")
    def test_ignore_sphinx_directives(self) -> None:
        """Test `check` with sphinx directives to ignore."""
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

"""
            ),
        )

    def test_check_doctest(self) -> None:
        """Test `check` with doctest."""
        self.assert_lines_equal(
            [5],
            rstcheck.check(
                """\
Testing
=======

>>> x = 1
>>>> x
1
"""
            ),
        )

    @staticmethod
    def test_check_doctest_do_not_crash_when_indented() -> None:
        """Test `check` does not crash with intended doctest.

        docutils does not provide line number when indented.
        """
        list(
            rstcheck.check(
                """\
Testing
=======

    >>> x = 1
    >>>> x
    1
"""
            )
        )

    def test_check_doctest_with_ignore(self) -> None:
        """Test `check` with doctest and ignore."""
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
"""
            ),
        )

    @unittest.skipIf(rstcheck.SPHINX_INSTALLED, "Does not work with Sphinx")
    def test_check_doctest_in_code(self) -> None:
        """Test `check` with doctest in code."""
        self.assert_lines_equal(
            [7],
            rstcheck.check(
                """\
Testing
=======

.. code:: doctest

    >>> x = 1
    >>>> x
    1
"""
            ),
        )

    def test_check_doctest_in_code_block(self) -> None:
        """Test `check` with doctest in code block."""
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
"""
            ),
        )

    def test_check_doctest_in_python_code_block(self) -> None:
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
"""
            ),
        )


def main() -> None:
    """Run test suite."""
    with rstcheck.enable_sphinx_if_possible():
        unittest.main()


if __name__ == "__main__":
    main()
