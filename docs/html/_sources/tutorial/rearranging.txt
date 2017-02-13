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

  >>> [1, 2, 3, 4] >> Slice(2) >> Collect()
  [1, 2]

If ``start`` and ``stop`` are provided the elements from ``start`` index
to ``stop`` index (excluded) are extracted:

  >>> [1, 2, 3, 4] >> Slice(1, 3) >> Collect()
  [2, 3]

Finally the third parameter allows to specify a ``stride``:

  >>> [1, 2, 3, 4] >> Slice(0, 4, 2) >> Collect()
  [1, 3]



TODO
-----

  Chunk, Cycle, Dedupe, Permutate, Combine