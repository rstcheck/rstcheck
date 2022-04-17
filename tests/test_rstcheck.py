"""Test suite for rstcheck."""

import typing

import pytest

import rstcheck


# We don't do this in the module itself to avoid mutation.
rstcheck.ignore_sphinx()


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_parse_gcc_style_error_message() -> None:
    """Test `parse_gcc_style_error_message`."""
    error_tuple = (32, "error message")
    pre_parse_err_msg = "filename:32:7: error message"

    result = rstcheck.parse_gcc_style_error_message(pre_parse_err_msg, filename="filename")

    assert error_tuple == result


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_parse_gcc_style_error_message_with_no_column() -> None:
    """Test `parse_gcc_style_error_message` with no column."""
    error_tuple = (32, "error message")
    pre_parse_err_msg = "filename:32: error message"

    result = rstcheck.parse_gcc_style_error_message(
        pre_parse_err_msg, filename="filename", has_column=False
    )

    assert error_tuple == result


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_parse_gcc_style_error_message_with_parsing_error_missing_file() -> None:
    """Test `parse_gcc_style_error_message` raising exceptions."""
    pre_parse_err_msg = ":32:3 error message"

    with pytest.raises(ValueError, match="Message cannot be parsed."):
        rstcheck.parse_gcc_style_error_message(pre_parse_err_msg, filename="filename")


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_parse_gcc_style_error_message_with_parsing_error_missing_column() -> None:
    """Test `parse_gcc_style_error_message` raising exceptions."""
    pre_parse_err_msg = "filename:32: error message"

    with pytest.raises(IndexError):
        rstcheck.parse_gcc_style_error_message(
            pre_parse_err_msg, filename="filename", has_column=True
        )


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_check() -> None:
    """Test `check`."""
    line_numbers = {
        6,
    }

    result = rstcheck.check(
        """\
Test
====

.. code:: python

    print(
"""
    )

    assert line_numbers == set(dict(result))


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_check_code_block() -> None:
    """Test `check` with python code block."""
    line_numbers = {
        6,
    }

    result = rstcheck.check(
        """\
Test
====

.. code-block:: python

    print(
"""
    )

    assert line_numbers == set(dict(result))


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_check_json() -> None:
    """Test `check` with json."""
    line_numbers = {
        7,
    }

    result = rstcheck.check(
        """\
Test
====

.. code-block:: json

    {
        'abc': 123
    }
"""
    )

    assert line_numbers == set(dict(result))


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_check_json_with_ignore() -> None:
    """Test `check` with json and ignore."""
    line_numbers: typing.Set[int] = set()

    result = rstcheck.check(
        """\
Test
====

.. code-block:: json

    {
        'abc': 123
    }

.. rstcheck: ignore-language=json,python,rst
"""
    )

    assert line_numbers == set(dict(result))


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_check_json_with_unmatched_ignores_only() -> None:
    """Test `check` with json and unmatched ignore."""
    line_numbers = {
        7,
    }

    result = rstcheck.check(
        """\
Test
====

.. code-block:: json

    {
        'abc': 123
    }

.. rstcheck: ignore-language=cpp,python,rst
"""
    )

    assert line_numbers == set(dict(result))


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_check_json_with_bad_ignore() -> None:
    """Test `check` with json and bad ignore."""
    line_numbers = {
        7,
        10,
    }

    result = rstcheck.check(
        """\
Test
====

.. code-block:: json

    {
        'abc': 123
    }

.. rstcheck: ignore-language json,python,rst
"""
    )

    assert line_numbers == set(dict(result))


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_check_xml() -> None:
    """Test `check` with xml."""
    line_numbers = {
        8,
    }

    result = rstcheck.check(
        """\
Test
====

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <root>
       </abc>123<abc>
    </root>
"""
    )

    assert line_numbers == set(dict(result))


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_check_xml_with_ignore() -> None:
    """Test `check` with xml and ignore."""
    line_numbers: typing.Set[int] = set()

    result = rstcheck.check(
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
    )

    assert line_numbers == set(dict(result))


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_check_xml_with_unmatched_ignores_only() -> None:
    """Test `check` with xml and unmatched ignore."""
    line_numbers = {
        8,
    }

    result = rstcheck.check(
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
    )

    assert line_numbers == set(dict(result))


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_check_xml_with_bad_ignore() -> None:
    """Test `check` with xml and bad ignore."""
    line_numbers = {
        8,
        11,
    }

    result = rstcheck.check(
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
    )

    assert line_numbers == set(dict(result))


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_check_with_extra_blank_lines_before() -> None:
    """Test `check` with python and extra blank lines before."""
    line_numbers = {
        8,
    }

    result = rstcheck.check(
        """\
Test
====

.. code-block:: python



    print(
"""
    )

    assert line_numbers == set(dict(result))


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_check_with_extra_blank_lines_after() -> None:
    """Test `check` with python and extra blank lines after."""
    line_numbers = {
        6,
    }

    result = rstcheck.check(
        """\
Test
====

.. code-block:: python

    print(



"""
    )

    assert line_numbers == set(dict(result))


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_check_with_extra_blank_lines_before_and_after() -> None:
    """Test `check` with python and extra blank lines before and after."""
    line_numbers = {
        8,
    }

    result = rstcheck.check(
        """\
Test
====

.. code-block:: python



    print(



"""
    )

    assert line_numbers == set(dict(result))


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_check_rst() -> None:
    """Test `check` with rst."""
    line_numbers = {
        2,
    }

    result = rstcheck.check(
        """\
Test
===
"""
    )

    assert line_numbers == set(dict(result))


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_check_rst_report_level() -> None:
    """Test `check` with rst and set report level."""
    line_numbers: typing.Set[int] = set()

    result = rstcheck.check(
        """\
Test
===
""",
        report_level=5,
    )

    assert line_numbers == set(dict(result))


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_check_nested_rst() -> None:
    """Test `check` with nested rst."""
    line_numbers = {
        32,
    }

    result = rstcheck.check(
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
    )

    assert line_numbers == set(dict(result))


@pytest.mark.skipif(not rstcheck.SPHINX_INSTALLED, reason="Requires Sphinx")
@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_ignore_sphinx_directives() -> None:
    """Test `check` with sphinx directives to ignore."""
    line_numbers: typing.Set[int] = set()

    result = rstcheck.check(
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
    )

    assert line_numbers == set(dict(result))


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_check_doctest() -> None:
    """Test `check` with doctest."""
    line_numbers = {
        5,
    }

    result = rstcheck.check(
        """\
Testing
=======

>>> x = 1
>>>> x
1
"""
    )

    assert line_numbers == set(dict(result))


@pytest.mark.usefixtures("enable_sphinx_if_possible")
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
    )  # act


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_check_doctest_with_ignore() -> None:
    """Test `check` with doctest and ignore."""
    line_numbers: typing.Set[int] = set()

    result = rstcheck.check(
        """\
Testing
=======

>>> x = 1
>>>> x
1

.. rstcheck: ignore-language=doctest
"""
    )

    assert line_numbers == set(dict(result))


@pytest.mark.skipif(rstcheck.SPHINX_INSTALLED, reason="Does not work with Sphinx")
@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_check_doctest_in_code() -> None:
    """Test `check` with doctest in code."""
    line_numbers = {
        7,
    }

    result = rstcheck.check(
        """\
Testing
=======

.. code:: doctest

    >>> x = 1
    >>>> x
    1
"""
    )

    assert line_numbers == set(dict(result))


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_check_doctest_in_code_block() -> None:
    """Test `check` with doctest in code block."""
    line_numbers = {
        7,
    }

    result = rstcheck.check(
        """\
Testing
=======

.. code-block:: doctest

    >>> x = 1
    >>>> x
    1
"""
    )

    assert line_numbers == set(dict(result))


@pytest.mark.usefixtures("enable_sphinx_if_possible")
def test_check_doctest_in_python_code_block() -> None:
    """I'm not sure if this is correct, but I've seen people do it."""
    line_numbers = {
        7,
    }

    result = rstcheck.check(
        """\
Testing
=======

.. code-block:: python

    >>> x = 1
    >>>> x
    1
"""
    )

    assert line_numbers == set(dict(result))
