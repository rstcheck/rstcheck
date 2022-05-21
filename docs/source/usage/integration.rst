Integration
===========

``rstcheck`` can be integrated and used with other tools.


Usage in Vim
------------


Using with Syntastic_:
~~~~~~~~~~~~~~~~~~~~~~

.. code:: vim

    let g:syntastic_rst_checkers = ['rstcheck']


Using with ALE_:
~~~~~~~~~~~~~~~~

Just install ``rstcheck`` and make sure is on your path.


Use as a pre-commit hook
------------------------

Add this to your ``.pre-commit-config.yaml``

.. code:: yaml

    -   repo: https://github.com/myint/rstcheck
        rev: ''  # Use the sha / tag you want to point at
        hooks:
        -   id: rstcheck


Use with Mega-Linter
--------------------

Just install Mega-Linter_ in your repository, rstcheck_ is part of
the 70 linters activated out of the box.


.. _Syntastic: https://github.com/vim-syntastic/syntastic
.. _ALE: https://github.com/dense-analysis/ale
.. _Mega-Linter: https://megalinter.github.io/latest/
.. _rstcheck: https://megalinter.github.io/latest/descriptors/rst_rstcheck/
