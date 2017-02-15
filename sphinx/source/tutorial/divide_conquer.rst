.. _divide_conquer:

Divide and conquer
===================

It is frequently necessary to either split a data flow into multiple flows
or combine data flows. The following nuts are specifically designed for this
purpose. In this context the :ref:`Partition` and the :ref:`MapMulti` nuts
might be of interest as well.


[TODO: Make Concat/Zip/Interleave sources? Concat(*iterables)]

Unzip
^^^^^

iterable >> Unzip()

Same as zip(*iterable) but returns iterators for noiter=False.

  >>> from nutsflow import *

  >>> [(1, 2, 3), (4, 5, 6)] >> Unzip() >> Map(tuple) >> Collect()
  [(1, 4), (2, 5), (3, 6)]


Zip
^^^

iterable >> Zip(*iterables)

Zip elements of iterable with elements of given iterables
Zip finishes when shortest iterable is exhausted.
See https://docs.python.org/2/library/itertools.html#itertools.izip
And https://docs.python.org/2/library/itertools.html#itertools.izip_longest

  >>> [0, 1, 2] >> Zip('abc') >> Collect()
  [(0, 'a'), (1, 'b'), (2, 'c')]

  >>> '12' >> Zip('abcd', '+-') >> Collect()
  [('1', 'a', '+'), ('2', 'b', '-')]


Interleave
^^^^^^^^^^

iterable >> Interleave(*iterables)

Interleave elements of iterable with elements of given iterables.
Similar to iterable >> Zip(*iterables) >> Flatten() but longest iterable
determines length of interleaved iterator.

  >>> Range(5) >> Interleave('abc') >> Collect()
  [0, 'a', 1, 'b', 2, 'c', 3, 4]

  >>> '12' >> Interleave('abcd', '+-') >> Collect()
  ['1', 'a', '+', '2', 'b', '-', 'c', 'd']


Tee
^^^

iterable >> Tee([n=2])

Return n independent iterators from a single iterable. Can consume large
amounts of memory if iterable is large and tee's are not processed in
parallel.
See https://docs.python.org/2/library/itertools.html#itertools.tee

  >>> it1, it2  = [1, 2, 3] >> Tee(2)
  >>> it1 >> Collect()
  [1, 2, 3]

  >>> it2 >> Collect()
  [1, 2, 3]


Concat
^^^^^^

iterable >> Concat(*iterables)

Concatenate iterables.

  >>> Range(5) >> Concat('abc') >> Collect()
  [0, 1, 2, 3, 4, 'a', 'b', 'c']

  >>> '12' >> Concat('abcd', '+-') >> Collect()
  ['1', '2', 'a', 'b', 'c', 'd', '+', '-']



