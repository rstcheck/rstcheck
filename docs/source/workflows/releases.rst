.. highlight:: console

Releases
========

Release workflow
----------------

When enough changes and additions or time important fixes have accumulated on the
``master`` branch its time for a new release. The exact time is subject to the
judgment of the mastertainer(s).


.. note::

  Before starting the process of creating a new release make sure that all CI pipelines
  are green for the current commit.

1. Check if the ``CHANGELOG.md`` is up-to-date and all changes are noted.

2. Run ``prep_release.py`` script to bump version, finalize ``CHANGELOG.md``,
   commit the changes and create a new git tag::

    $ python3 prep_release.py --increase-type <TYPE>

  For the increase type there are three options:

     - ``patch`` / ``bugfix``:
       for changes that **do not** add new functionality and are backwards compatible
     - ``minor`` / ``feature``:
       for changes that **do** add new functionality and are backwards compatible
     - ``major`` / ``breaking``:
       for changes that are **not** backwards compatible

3. Build the sdist and wheel::

    $ poetry build

4. Publish package::

   $ poetry publish

5. Push the commit and tag to github::

    $ git push --follow-tags

.. highlight:: default
