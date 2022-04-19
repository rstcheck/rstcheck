Testing
=======

.. |BAZ_ID| replace:: baz

The tables below are properly formatted, but contain substitution references
that are not defined in the document. If those substitutions are not ignored
through configuration option, rstcheck should complain about the missing
definitions. If they *are* marked as ignored through command line or
configuration file, then everything should be good.

In the past, rstcheck would fail to validate such tables when the user would
ignore the missing references. This was because substitution references were
simply replaced with "None", potentially leaving cells with a padding of an
incorrect size.

First, let's try with a grid table.

+------+------------+
| Name | Identifier |
+======+============+
| Foo  | |FOO_ID|   |
+------+------------+
| Bar  | |BAR_ID|   |
+------+------------+
| Baz  | |BAZ_ID|   |
+------+------------+

Take two: with a simple table.

==== ==========
Name Identifier
==== ==========
Foo  |FOO_ID|
Bar  |BAR_ID|
Baz  |BAZ_ID|
==== ==========
