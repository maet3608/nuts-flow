.. _rearranging:

Rearranging data
================

Another common need is to rearrange or restructure data. The following nuts
can help with that.

>>> from nutsflow import *


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


Cycle
-----

Sometimes it is necessary to repeatedly process an iterable. ``Cycle`` takes
all elements from its input iterable, stores them in memory and returns an
iterator that cycles through the elements indefinitely. Here an example that
cycles through 1, 2, 3 and takes the first 10 elements:

>>> [1, 2, 3] >> Cycle() >> Take(10) >> Collect()
[1, 2, 3, 1, 2, 3, 1, 2, 3, 1]

Note that ``Cycle`` will consume large amounts of memory if the input iterable
is large.


Permutate
---------

``Permutate([,r])`` returns successive ``r`` length permutations of
the elements in the input iterable.

>>> [1, 2, 3] >> Permutate(2) >> Collect()
[(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]

Maybe a more interesting example: What is the number of distinctive
palindroms for a given string:

>>> IsPalindrom = nut_filter(lambda x: x == x[::-1])
>>> 'devoved' >> Permutate() >> IsPalindrom() >> Collect(set) >> Count()
6

If no permutation size ``r`` is specified then all possible full-length
permutations are generated (r!) and the computation will not finish in
any reasonable time for non-small ``r``'s!


Combine
-------

``Combine(r)`` return ``r`` length subsequences of the elements from the
input iterable.

>>> [1, 2, 3] >> Combine(2) >> Collect()
[(1, 2), (1, 3), (2, 3)]

Note that ``Combine(r)`` returns a subset of ``Permutate(r)`` with permutations
where the order of the elements (as given in the input iterable) is preserved.



Dedupe
------

A very common task is to remove all duplicates from a data set.
``Dedupe([key])`` performs this task and also takes a key function
that defines which elements are treated as equal.

``Dedupe()`` preserves the order of the element in the input. See the
following example:

>>> [2, 3, 1, 1, 2, 4] >> Dedupe() >> Collect()
[2, 3, 1, 4]

More complex data often require a more sophisticated definition of equality
and the key functions provides this:

>>> data = [(1, 'a'), (2, 'a'), (3, 'b')]
>>> data >> Dedupe(lambda (x, y): y) >> Collect()
[(1, 'a'), (3, 'b')]


``Dedupe()`` memorizes all unique elements of the input iterable in a set
and can potentially consume large amounts of memory!
