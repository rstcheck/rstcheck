Inline ignore comment example
=============================

This is a copy of ``without_inline_ignore.rst`` with ignore comments below.

.. custom-directive::

:custom-role:`example`

.. code:: python

    print(

|unmatched-substitution|


.. rstcheck: ignore-directives=custom-directive
.. rstcheck: ignore-roles=custom-role
.. rstcheck: ignore-languages=python
.. rstcheck: ignore-substitutions=unmatched-substitution
