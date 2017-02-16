.. _divide_conquer:

Divide and conquer
===================

It is frequently necessary to either split a data flow into multiple flows
or combine data flows. The following nuts are specifically designed for this
purpose. In this context the :ref:`Partition` and the :ref:`MapMulti` nuts
might be of interest as well.



Zip
^^^

``Zip(*iterables)`` combines two or more iterables like a *zipper* taking at
every step an element from each iterable and outputting a tuple of the
grouped elements. Here an example

  >>> from nutsflow import *

  >>> numbers = [0, 1, 2]
  >>> letters = ['a', 'b', 'c']
  >>> numbers >> Zip(letters) >> Collect()
  [(0, 'a'), (1, 'b'), (2, 'c')]

``Zip`` finishes when shortest iterable is exhausted. See

  >>> Range(100) >> Zip('abc') >> Collect()
  [(0, 'a'), (1, 'b'), (2, 'c')]

Note that ``Zip`` can zip more than two iterables:

  >>> '12' >> Zip('ab', '+-') >> Collect()
  [('1', 'a', '+'), ('2', 'b', '-')]

If the output of ``Zip`` is required to be flat ``Flatten`` can be called

  >>> [0, 1, 2] >> Zip('abc') >> Flatten() >> Collect()
  [0, 'a', 1, 'b', 2, 'c']

but using :ref:`Interleave` is simpler in this case.


Unzip
^^^^^

``Unzip(container=None)`` reverses a ``Zip`` operation:

  >>> numbers, letters = [0, 1, 2] >> Zip('abc') >> Unzip()
  >>> list(numbers)
  [0, 1, 2]
  >>> list(letters)
  ['a', 'b', 'c']

Per default ``Unzip`` returns iterators but often the results are required
as lists or other collections (see above). ``Unzip`` allows to provide a
container to collect the results:

  >>> [0, 1, 2] >> Zip('abc') >> Unzip(list) >> Collect()
  [[0, 1, 2], ['a', 'b', 'c']]

This equivalent to ``Unzip() >> Map(list) >> Collect()`` but shorter.



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



