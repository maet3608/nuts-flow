.. _sources:

Reading from Sources
====================

All data flows start with a *source*. Sources are Python iterables and a small
set of specific nuts. As a general rule, sources must appear on the left side
of the ``>>`` operator and can never appear on the right side.


Iterables
---------

Some examples of Python iterables and iterators that can be used as sources:

  >>> from nutsflow import *

  >>> xrange(5) >> Collect()
  [0, 1, 2, 3, 4]

  >>> ['a', 'ab', 'abc'] >> Map(len) >> Collect()
  [1, 2, 3]

  >>> 'text' >> Map(lambda c: c.upper()) >> Join()
  'TEXT'

  >>> {1:'one', 2:'two'} >> Collect()
  [1, 2]

  >>> {1:'one', 2:'two'}.iteritems() >> Collect()
  [(1, 'one'), (2, 'two')]

.. code::

  with open(filepath) as lines:
    lines >> Filter(lambda l: l.startswith('ERR')) >> Print() >> Consume()


Source nuts
-----------

**nuts-flow** has a few special source nuts.

Range
^^^^^

``Range(start [,end [, step]])`` essential operates the same as ``xrange``
but depletes. The following examples demonstrates the difference:

  >>> numbers = Range(5)
  >>> numbers >> Head(3)
  [0, 1, 2]
  >>> numbers >> Head(3)
  [3, 4]
  >>> numbers >> Head(3)
  []

Subsequent calls deplete the numbers iterator created with ``Range``, while
``xrange`` returns a new iterator every time when called and does not deplete:

  >>> numbers = xrange(5)
  >>> numbers >> Head(3)
  [0, 1, 2]
  >>> numbers >> Head(3)
  [0, 1, 2]


Enumerate
^^^^^^^^^

``Enumerate(start=0 [, step])`` returns an iterator over increasing integer
numbers. In contrast to :ref:`Range` it does not have an upper limit and
iterates indefinitely.

  >>> Enumerate(1) >> Zip('abc') >> Collect()
  [(1, 'a'), (2, 'b'), (3, 'c')]

Often ``Enumerate`` is used to add line numbers to the lines of a file:

.. code::

  # Collect line numbers of empty lines
  with open(filepath) as lines:
    (Enumerate() >> Zip(lines) >> Filter(lambda (i,l): not l) >>
    Get(0) >> Collect())


Product
^^^^^^^

``Product`` is the functional equivalent of a nested loop. It generates the
cartesian product of the input iterables. For instance, the following example
returns the coordinates of a 2x3 grid:

  >>> Product(Range(2), Range(3)) >> Collect()
  [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]


Repeat
^^^^^^

Repeat(object)

Return given object repeatedly. See itertools.repeat

>>> Repeat(1, 3) >> Collect()
[1, 1, 1]

>>> Repeat(1) >> Take(4) >> Collect()
[1, 1, 1, 1]



ReadCSV
^^^^^^^

        ReadCSV(filepath, columns, skipheader, fmtfunc, **kwargs)

        Read data in Comma Separated Format (CSV) from file.
        See also CSVWriter.
        Can also read Tab Separated Format (TSV) be providing the
        corresponding delimiter. Note that in the docstring below
        delimiter is '\\t' but in code it should be '\t'. See unit tests.

        >>> from nutsflow import Collect
        >>> filepath = 'tests/data/data.csv'
        >>> with ReadCSV(filepath, skipheader=1, fmtfunc=int) as reader:
        ...     reader >> Collect()
        [(1, 2, 3), (4, 5, 6)]

        >>> with ReadCSV(filepath, (2, 1), 1, int) as reader:
        ...     reader >> Collect()
        [(3, 2), (6, 5)]

        >>> filepath = 'tests/data/data.tsv'
        >>> with ReadCSV(filepath, skipheader=1, fmtfunc=int,
        ...                delimiter='\\t') as reader:
        ...     reader >> Collect()
        [(1, 2, 3), (4, 5, 6)]
