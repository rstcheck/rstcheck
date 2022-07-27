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

Add this to your ``.pre-commit-config.yaml``:

.. code:: yaml

    -   repo: https://github.com/rstcheck/rstcheck
        rev: ''  # Use the sha / tag you want to point at
        hooks:
        -   id: rstcheck
            additional_dependencies: []  # can be omitted if empty

You may want to specify a ``rstcheck-core`` version or range, if you depend on a feature which was
added after the current minimal version of ``rstcheck-core``.
Simply add e.g. ``"rstcheck-core==v1.0.0"`` to the list for ``additional_dependencies``.


Use with Mega-Linter
--------------------

Just install Mega-Linter_ in your repository, rstcheck_ is part of
the 70 linters activated out of the box.


.. _Syntastic: https://github.com/vim-syntastic/syntastic
.. _ALE: https://github.com/dense-analysis/ale
.. _Mega-Linter: https://oxsecurity.github.io/megalinter/latest/
.. _rstcheck: https://oxsecurity.github.io/megalinter/latest/descriptors/rst_rstcheck/
