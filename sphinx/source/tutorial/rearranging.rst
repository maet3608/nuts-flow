.. _rearranging:

Rearranging data
================

Another common need is to rearrange or restructure data. The following nuts
can help with that.


Slice
-----

``Slice([start,] stop, stride]])``, as the name indicates, takes a slice of the
data. Similar to Python's
`slicing <https://docs.python.org/2.3/whatsnew/section-slices.html>`_
operation it extracts a section of the data. If not ``start`` or ``stride``
are provided, ``Slice`` extracts the first ``stop`` elements:

  >>> from nutsflow import *

  >>> [1, 2, 3, 4] >> Slice(2) >> Collect()
  [1, 2]

If ``start`` and ``stop`` are provided the elements from ``start`` index
to ``stop`` index (excluded) are extracted:

  >>> [1, 2, 3, 4] >> Slice(1, 3) >> Collect()
  [2, 3]

Finally the third parameter allows to specify a ``stride``. In this example
every second element in the slice starting at index 0 and ending at index 4
(exclusive) is extracted:

  >>> [1, 2, 3, 4] >> Slice(0, 4, 2) >> Collect()
  [1, 3]


Chunk
-----

``Chunk(n)`` is a nut to group data in chunks of size ``n``:

  >>> Range(5) >> Chunk(2) >> Map(list) >> Collect()
  [[0, 1], [2, 3], [4]]


Note that each chunk is an iterator over the elements in the chunk,
which is why ``Map(list)`` is required to convert the chunks to printable lists.
A more interesting example might be the sum of the elements within each chunk:

  >>> Range(5) >> Chunk(2) >> Map(sum) >> Collect()
  [1, 5, 4]





TODO
-----

  Cycle, Dedupe, Permutate, Combine