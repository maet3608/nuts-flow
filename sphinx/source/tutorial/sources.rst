.. _sources:

Reading from Sources
====================

TODO

Iterables
---------

Sources are all iterables
range, xrange, generator, iterator, list, set, dictionary, ...

.. code::

  with open(filepath) as lines:
    lines >> Filter(lamdba l: l.startswith('ERR')) >> Print() >> Consume()


Source nuts
-----------

Range
^^^^^

Note: Depletes in contrast to Python's ``range`` and ``xrange``


ReadCSV
^^^^^^^