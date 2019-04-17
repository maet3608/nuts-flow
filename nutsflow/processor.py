"""
.. module:: processor
   :synopsis: Nuts that process iterables and return iterables.
"""
from __future__ import print_function, division

import tempfile
import shutil
import os
import time
import six
import sys

import os.path as osp
import itertools as itt
import random as rnd
import multiprocessing as mp
import collections as cl

from inspect import isfunction, ismethod, isbuiltin
from six.moves import cPickle as pickle
from six.moves import map, filter, filterfalse, zip, range
from . import iterfunction as itf
from .base import Nut, NutFunction
from .common import as_tuple, as_list, as_set, console, timestr, is_iterable
from .factory import nut_processor
from .function import Identity
from .sink import Consume, Collect, Head


@nut_processor
def Take(iterable, n):
    """
    iterable >> Take(n)

    Return first n elements of iterable

    >>> from nutsflow import Collect

    >>> [1, 2, 3, 4] >> Take(2) >> Collect()
    [1, 2]

    :param iterable iterable: Any iterable
    :param int n: Number of elements to take
    :return: First n elements of iterable
    :rtype: iterator
    """
    return itf.take(iterable, n)


@nut_processor
def Slice(iterable, start=None, *args, **kwargs):
    """
    iterable >> Slice([start,] stop[, stride])

    Return slice of elements from iterable.
    See https://docs.python.org/2/library/itertools.html#itertools.islice
    
    >>> from nutsflow import Collect
     
    >>> [1, 2, 3, 4] >> Slice(2) >> Collect()
    [1, 2]

    >>> [1, 2, 3, 4] >> Slice(1, 3) >> Collect()
    [2, 3]

    >>> [1, 2, 3, 4] >> Slice(0, 4, 2) >> Collect()
    [1, 3]

    :param iterable iterable: Any iterable
    :param int start: Start index of slice.
    :param int stop: End index of slice.
    :param int step: Step size of slice.
    :return: Elements sliced from iterable
    :rtype: iterator
    """
    return itt.islice(iterable, start, *args, **kwargs)


@nut_processor
def Window(iterable, n=2):
    """
    iterable >> Window(n)

    Sliding window of size n over elements in iterable.

    >>> [1, 2, 3, 4] >> Window() >> Collect()
    [(1, 2), (2, 3), (3, 4)]

    >>> [1, 2, 3, 4] >> Window(3) >> Collect()
    [(1, 2, 3), (2, 3, 4)]

    >>> 'test' >> Window(2) >> Map(''.join) >> Collect()
    ['te', 'es', 'st']

    :param iterable iterable: Any iterable
    :param int n: Size of window
    :return: iterator with tuples of length n
    :rtype: iterator over tuples
    """
    it = iter(iterable)
    win = cl.deque(it >> Take(n), n)
    yield tuple(win)
    for e in it:
        win.append(e)
        yield tuple(win)


@nut_processor
def Concat(iterable, *iterables):
    """
    iterable >> Concat(*iterables)

    Concatenate iterables.

    >>> from nutsflow import Range, Collect

    >>> Range(5) >> Concat('abc') >> Collect()
    [0, 1, 2, 3, 4, 'a', 'b', 'c']

    >>> '12' >> Concat('abcd', '+-') >> Collect()
    ['1', '2', 'a', 'b', 'c', 'd', '+', '-']

    :param iterable iterable: Any iterable
    :param iterable iterables: Iterables to concatenate
    :return: Concatenated iterators
    :rtype: iterator
    """
    return itt.chain(iterable, *iterables)


@nut_processor
def Interleave(iterable, *iterables):
    """
    iterable >> Interleave(*iterables)

    Interleave elements of iterable with elements of given iterables.
    Similar to iterable >> Zip(*iterables) >> Flatten() but longest iterable
    determines length of interleaved iterator.

    >>> from nutsflow import Range, Collect
    >>> Range(5) >> Interleave('abc') >> Collect()
    [0, 'a', 1, 'b', 2, 'c', 3, 4]

    >>> '12' >> Interleave('abcd', '+-') >> Collect()
    ['1', 'a', '+', '2', 'b', '-', 'c', 'd']

    :param iterable iterable: Any iterable
    :param iterable iterables: Iterables to interleave
    :return: Iterator over interleaved elements.
    :rtype: iterator
    """
    return itf.interleave(iterable, *iterables)


@nut_processor
def Zip(iterable, iterable2=None, *iterables):
    """
    iterable >> Zip(*iterables)

    Zip elements of iterable with elements of given iterables.
    Zip finishes when shortest iterable is exhausted.
    See https://docs.python.org/2/library/itertools.html#itertools.izip
    And https://docs.python.org/2/library/itertools.html#itertools.izip_longest

    >>> from nutsflow import Collect

    >>> [0, 1, 2] >> Zip('abc') >> Collect()
    [(0, 'a'), (1, 'b'), (2, 'c')]

    >>> '12' >> Zip('abcd', '+-') >> Collect()
    [('1', 'a', '+'), ('2', 'b', '-')]

    :param iterable iterable: Any iterable
    :param iterable iterables: Iterables to zip
    :return: Zipped elements from iterables.
    :rtype: iterator over tuples
    """
    return zip(iterable, iterable2, *iterables)


@nut_processor
def ZipWith(iterable, f, *iterables):
    """
    iterable >> ZipWith(f, *iterables)

    Zips the given iterables, unpacks them and applies the given function.

    >>> add = lambda a, b: a + b
    >>> [1, 2, 3] >> ZipWith(add, [2, 3, 4]) >> Collect()
    [3, 5, 7]

    :param iterable iterable: Any iterable
    :param iterable iterables: Any iterables
    :param function f: Function to apply to zipped input iterables
    :return: iterator of result of f() applied to zipped iterables
    :rtype: iterator
    """
    iterables = [iterable] + list(iterables)
    return itt.starmap(f, zip(*iterables))


@nut_processor
def Append(iterable, items):
    """
    iterable >> Append(items)

    Append item(s) to lists/tuples in iterable.

    >>> [(1, 2), (3, 4)] >> Append('X') >> Collect()
    [(1, 2, 'X'), (3, 4, 'X')]

    >>> items = ['a', 'b']
    >>> [(1, 2), (3, 4)] >> Append(items) >> Collect()
    [(1, 2, 'a'), (3, 4, 'b')]

    >>> items = [('a', 'b'), ('c', 'd')]
    >>> [(1, 2), (3, 4)] >> Append(items) >> Collect()
    [(1, 2, 'a', 'b'), (3, 4, 'c', 'd')]

    >>> from nutsflow import Enumerate
    >>> [(1, 2), (3, 4)] >> Append(Enumerate()) >> Collect()
    [(1, 2, 0), (3, 4, 1)]

    :param iterable iterable iterable: Any iterable over tuples or lists
    :param iterable|object items: A single object or an iterable over objects.
    :return: iterator where items are appended to the iterable elements.
    :rtype: iterator over tuples
    """
    items = items if is_iterable(items) else itt.repeat(items)
    for elem, item in zip(iterable, items):
        yield tuple(elem) + as_tuple(item)


@nut_processor
def Insert(iterable, index, items):
    """
    iterable >> Insert(index, items)

    Insert item(s) into lists/tuples in iterable.

    >>> [(1, 2), (3, 4)] >> Insert(1, 'X') >> Collect()
    [(1, 'X', 2), (3, 'X', 4)]

    >>> items = ['a', 'b']
    >>> [(1, 2), (3, 4)] >> Insert(2, items) >> Collect()
    [(1, 2, 'a'), (3, 4, 'b')]

    >>> items = [('a', 'b'), ('c', 'd')]
    >>> [(1, 2), (3, 4)] >> Insert(1, items) >> Collect()
    [(1, 'a', 'b', 2), (3, 'c', 'd', 4)]

    >>> from nutsflow import Enumerate
    >>> [(1, 2), (3, 4)] >> Insert(0, Enumerate()) >> Collect()
    [(0, 1, 2), (1, 3, 4)]

    :param iterable iterable iterable: Any iterable over tuples or lists
    :param int index: Index at which position items are inserted.
    :param iterable|object items: A single object or an iterable over objects.
    :return: iterator where items are inserted into the iterable elements.
    :rtype: iterator over tuples
    """
    items = items if is_iterable(items) else itt.repeat(items)
    for elem, item in zip(iterable, items):
        elem = list(elem)
        head, tail = elem[:index], elem[index:]
        yield tuple(head + as_list(item) + tail)


Dedupe = nut_processor(itf.unique)
"""
iterable >> Dedupe([key])

Return only unique elements in iterable. Can have very high memory consumption
if iterable is long and many elements are unique!

>>> [2,3,1,1,2,4] >> Dedupe() >> Collect()
[2, 3, 1, 4]

>>> data = [(1,'a'), (2,'a'), (3,'b')]
>>> data >> Dedupe(key=lambda (x,y): y) >> Collect()
[(1, 'a'), (3, 'b')]

>>> data >> Dedupe(_[1]) >> Collect()
[(1, 'a'), (3, 'b')]

:param iterable iterable: Any iterable, e.g. list, range, ...
:param key: Function used to compare for equality.
:return: Iterator over unique elements.
:rtype: Iterator
"""


@nut_processor
def Chunk(iterable, n, container=None):
    """
    iterable >> Chunk(n, container=None)

    Split iterable in chunks of size n, where each chunk is also an iterator
    if no container is provided.
    see also GroupBySorted(), ChunkWhen(), ChunkBy()

    >>> from nutsflow import Range, Map, Print, Join, Consume, Collect
    >>> Range(5) >> Chunk(2) >> Map(list) >> Print() >> Consume()
    [0, 1]
    [2, 3]
    [4]

    The code can be shortend by providing a container in Chunk():

    >>> Range(5) >> Chunk(2, list) >> Print() >> Consume()
    [0, 1]
    [2, 3]
    [4]

    >>> Range(6) >> Chunk(3, Join('_')) >> Print() >> Consume()
    0_1_2
    3_4_5

    >>> Range(6) >> Chunk(3, sum) >> Collect()
    [3, 12]

    :param iterable iterable: Any iterable, e.g. list, range, ...
    :param int n: Chunk size
    :param container container: Some container, e.g. list, set, dict
           that can be filled from an iterable
    :return: Chunked iterable
    :rtype: Iterator over iterators or containers
    """
    chunks = itf.chunked(iterable, n)
    return map(container, chunks) if container else chunks


class ChunkWhen(Nut):
    def __init__(self, func, container=None):
        """
        iterable >> ChunkWhen(func, container=None)

        Chunk iterable and create new chunk every time func returns True.
        see also GroupBySorted(), Chunk(), ChunkBy()

        >>> from nutsflow import Map, Join, Collect
        >>> func = lambda x: x == 1
        >>> [1,2,1,3,1,4,5] >> ChunkWhen(func, tuple) >> Collect()
        [(1, 2), (1, 3), (1, 4, 5)]

        >>> func = lambda x: x == 1
        >>> [1,2,1,3,1,4,5] >> ChunkWhen(func, sum) >> Collect()
        [3, 4, 10]

        >>> func = lambda x: x == '|'
        >>> '0|12|345|6' >> ChunkWhen(func, Join()) >> Collect()
        ['0', '|12', '|345', '|6']

        :param function func: Boolean function that indicates chunks.
            New chunk is created if return value is True.
        :param container container: Some container, e.g. list, set, dict
           that can be filled from an iterable
        """
        self.cnt = 0
        self.func = func
        self.container = container

    def _key(self, x):
        """ Return keys (= counter) for groups (=chunks)"""
        if self.func(x):
            self.cnt += 1
        return self.cnt

    def __rrshift__(self, iterable):
        """
        :param any iterable iterable: iterable to create chunks for.
        :return: Iterator over chunks, where each chunk is an iterator itself
                 if no container is provided
        :rtype: iterator over iterators or containers
        """
        return iterable >> ChunkBy(self._key, self.container)


@nut_processor
def ChunkBy(iterable, func, container=None):
    """
    iterable >> ChunkBy(func, container=None)

    Chunk iterable and create chunk every time func changes its return value.
    see also GroupBySorted(), Chunk(), ChunkWhen()

    >>> [1,1, 2, 3,3,3] >> ChunkBy(lambda x: x, tuple) >> Collect()
    [(1, 1), (2,), (3, 3, 3)]

    >>> [1,1, 2, 3,3,3] >> ChunkBy(lambda x: x < 3, tuple)  >> Collect()
    [(1, 1, 2), (3, 3, 3)]

    :param iterable iterable: Any iterable, e.g. list, range, ...
    :param function func: Functions the iterable is chunked by
    :param container container: Some container, e.g. list, set, dict
           that can be filled from an iterable
    :return: Chunked iterable
    :rtype: Iterator over iterators or containers
    """
    groupiter = itt.groupby(iterable, func)
    chunks = map(lambda t: t[1], groupiter)
    return map(container, chunks) if container else chunks


Cycle = nut_processor(itt.cycle)
"""
iterable >> Cycle()

Cycle through iterable indefinitely. Large memory consumption if iterable is
large!

>>> [1, 2] >> Cycle() >> Take(5) >> Collect()
[1, 2, 1, 2, 1]

:param iterable iterable: Any iterable, e.g. list, range, ...
:return: Cycled input iterable
:rtype: Iterator
"""


@nut_processor
def Flatten(iterable):
    """
    iterable >> Flatten()

    Flatten the iterables within the iterable and non-iterables are passed
    through. Only one level is flattened. Chain Flatten to flatten deeper
    structures.

    >>> from nutsflow import Collect
    >>> [(1, 2), (3, 4, 5), 6] >> Flatten() >> Collect()
    [1, 2, 3, 4, 5, 6]

    >>> [(1, (2)), (3, (4, 5)), 6] >> Flatten() >> Flatten() >> Collect()
    [1, 2, 3, 4, 5, 6]

    :param iterable iterable: Any iterable.
    :return: Flattened iterable
    :rtype: Iterator
    """
    for it in iterable:
        if hasattr(it, '__iter__'):
            for element in it:
                yield element
        else:
            yield it


@nut_processor
def FlattenCol(iterable, cols):
    """
    iterable >> FlattenCol(cols)

    Flattens the specified columns of the tuples/iterables within the iterable.
    Only one level is flattened.

    (1 3)  (5 7)
    (2 4)  (6 8)   >> FlattenCol((0,1) >>   (1 3)  (2 4)  (5 7)  (6 8)

    If a column contains a single element (instead of an iterable) it is 
    wrapped into a repeater. This allows to flatten columns that are iterable
    together with non-iterable columns, e.g.

    (1 3)  (6 7)
    (2  )  (  8)   >> FlattenCols((0,1) >>   (1 3)  (2 3)  (6 7)  (6 8)

    >>> from nutsflow import Collect
    >>> data = [([1, 2], [3, 4]), ([5, 6], [7, 8])]
    >>> data >> FlattenCol(0) >> Collect()
    [(1,), (2,), (5,), (6,)]

    >>> data >> FlattenCol((0, 1)) >> Collect()
    [(1, 3), (2, 4), (5, 7), (6, 8)]

    >>> data >> FlattenCol((1, 0)) >> Collect()
    [(3, 1), (4, 2), (7, 5), (8, 6)]

    >>> data >> FlattenCol((1, 1, 0)) >> Collect()
    [(3, 3, 1), (4, 4, 2), (7, 7, 5), (8, 8, 6)]

    >>> data = [([1, 2], 3), (6, [7, 8])]
    >>> data >> FlattenCol((0, 1)) >> Collect()
    [(1, 3), (2, 3), (6, 7), (6, 8)]

    :param iterable iterable: Any iterable.
    :params int|tuple columns: Column index or indices
    :return: Flattened columns of iterable
    :rtype: generator
    """
    cols = as_tuple(cols)
    get = lambda e: e if is_iterable(e) else itt.repeat(e)
    for es in iterable:
        for e in zip(*[get(es[c]) for c in cols]):
            yield e


FlatMap = nut_processor(itf.flatmap, 1)
"""
iterable >> FlatMap(func)

Map function on iterable and flatten. Equivalent to
iterable >> Map(func) >> Flatten()

>>> [[0], [1], [2]] >> FlatMap(_) >> Collect()
[0, 1, 2]

>>> [[0], [1], [2]] >> FlatMap(_ * 2) >> Collect()
[0, 0, 1, 1, 2, 2]

:param iterable iterable: Any iterable.
:param function func: Mapping function.
:return: Mapped and flattened iterable
:rtype: Iterator
"""

Map = nut_processor(map, 1)
"""
iterable >> Map(func, *iterables)

Map function on iterable.
See https://docs.python.org/2/library/itertools.html#itertools.imap

>>> [0, 1, 2] >> Map(_ * 2) >> Collect()
[0, 2, 4]

>>> ['ab', 'cde'] >> Map(len) >> Collect()
[2, 3]

>> [2, 3, 10] >> Map(pow, [5, 2, 3]) >> Collect()
[32, 9, 1000]

:param iterable iterable: Any iterable
:param iterables iterables: Any iterables.
:param function func: Mapping function.
:return: Mapped iterable
:rtype: Iterator
"""

Filter = nut_processor(filter, None)
"""
iterable >> Filter(func)

Filter elements from iterable based on predicate function.
See https://docs.python.org/2/library/itertools.html#itertools.ifilter

>>> [0, 1, 2, 3] >> Filter(_ < 2) >> Collect()
[0, 1]

:param iterable iterable: Any iterable
:param function func: Predicate function. Element is removed if False.
:return: Filtered iterable
:rtype: Iterator
"""

FilterFalse = nut_processor(filterfalse, None)
"""
iterable >> FilterFalse(func)

Filter elements from iterable based on predicate function.
Same as Filter but elements are removed (not kept) if predicate function
returns True.
See https://docs.python.org/2/library/itertools.html#itertools.ifilterfalse

>>> [0, 1, 2, 3] >> FilterFalse(_ >= 2) >> Collect()
[0, 1]

:param iterable iterable: Any iterable
:param function func: Predicate function. Element is removed if True.
:return: Filtered iterable
:rtype: Iterator
"""

@nut_processor
def FilterCol(iterable, columns, func):
    """
    iterable >> FilterCol(columns, func)

    Filter elements from iterable based on predicate function and
    specified column(s).

    >>> is_even = lambda n: n % 2 == 0
    >>> [(0, 'e'), (1, 'o'), (2, 'e')] >> FilterCol(0, is_even) >> Collect()
    [(0, 'e'), (2, 'e')]


    :param iterable iterable: Any iterable
    :param int|tuple columns: Column or columns to extract from each
        element before passing it on to the predicate function.
    :param function func: Predicate function. Element is removed if False.
    :return: Filtered iterable
    :rtype: Iterator
    """
    cols = as_tuple(columns)
    if len(cols) == 1:
        extract = lambda es: es[columns]
    else:
        extract = lambda es: [es[i] for i, e in enumerate(es) if i in cols]
    for es in iterable:
        if func(extract(es)):
            yield es

Partition = nut_processor(itf.partition)
"""
partition1, partition2 = iterable >> Partition(func)

Split iterable into two partitions based on predicate function

>>> smaller, larger = Range(5) >> Partition(_ < 3)
>>> smaller >> Collect()
[0, 1, 2]
>>> larger >> Collect()
[3, 4]

:param iterable: Any iterable, e.g. list, range, ...
:param pred: Predicate function.
:return: Partition iterators
:rtype: Two iterators
"""

TakeWhile = nut_processor(itt.takewhile, None)
"""
iterable >> TakeWhile(func)

Take elements from iterable while predicte function is True.
See https://docs.python.org/2/library/itertools.html#itertools.takewhile

>>> [0, 1, 2, 3, 0] >> TakeWhile(_ < 2) >> Collect()
[0, 1]

:param iterable iterable: Any iterable
:param function func: Predicate function.
:return: Iterable
:rtype: Iterator
"""


@nut_processor
def DropWhile(iterable, func):
    """
    iterable >> DropWhile(func)

    Skip elements in iterable while predicate function is True.

    >>> from nutsflow import _
    >>> [0, 1, 2, 3, 0] >> DropWhile(_ < 2) >> Collect()
    [2, 3, 0]

    :param iterable iterable: Any iterable
    :param function func: Predicate function.
    :return: Iterable
    :rtype: Iterator
    """
    return itt.dropwhile(func, iterable)


Permutate = nut_processor(itt.permutations)
"""
iterable >> Permutate([,r])

Return successive r length permutations of elements in the iterable.
See https://docs.python.org/2/library/itertools.html#itertools.permutations

>>> 'ABC' >> Permutate(2) >> Collect()
[('A', 'B'), ('A', 'C'), ('B', 'A'), ('B', 'C'), ('C', 'A'), ('C', 'B')]

:param iterable iterable: Any iterable
:param int r: Permutation of length r are generated.
              If r is not specified or is None, then r defaults
              to the length of the iterable and all possible full-length
              permutations are generated.
:return: Iterable over permutations
:rtype: Iterator
"""

Combine = nut_processor(itt.combinations)
"""
iterable >> Combine(r)

Return r length subsequences of elements from the input iterable.
See https://docs.python.org/2/library/itertools.html#itertools.combinations

>>> 'ABC' >> Combine(2) >> Collect()
[('A', 'B'), ('A', 'C'), ('B', 'C')]

>>> [1, 2, 3, 4] >> Combine(3) >> Collect()
[(1, 2, 3), (1, 2, 4), (1, 3, 4), (2, 3, 4)]

:param iterable iterable: Any iterable
:param int r: Length of combinations
:return: Iterable over combinations
:rtype: Iterator
"""

Tee = nut_processor(itt.tee)
"""
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

:param iterable iterable: Any iterable
:param int n: Number of iterators to return.
:return: n iterators
:rtype: (Iterator, ...)
"""


@nut_processor
def If(iterable, cond, if_nut, else_nut=Identity()):
    """
    iterable >> If(cond, if_nut, [,else_nut])

    Depending on condition cond execute if_nut or else_nut. Useful for
    conditional flows.

    >>> from nutsflow import Square, Collect

    >>> [1, 2, 3] >> If(True, Square()) >> Collect()
    [1, 4, 9]

    >>> [1, 2, 3] >> If(False, Square(), Take(1)) >> Collect()
    [1]

    :param iterable iterable: Any iterable
    :param bool cond: Boolean conditional value.
    :param Nut if_nut: Nut to be executed if cond == True
    :param Nut else_nut: Nut to be executed if cond == False
    :return: Result of if_nut or else_nut
    :rtype: Any
    """
    return iterable >> (if_nut if cond else else_nut)


@nut_processor
def Drop(iterable, n):
    """
    iterable >> Drop(n)

    Drop first n elements in iterable.

    >>> [1, 2, 3, 4] >> Drop(2) >> Collect()
    [3, 4]


    :param iterable iterable: Any iterable
    :param int n: Number of elements to drop
    :return: Iterator without dropped elements
    :rtype: iterator
    """
    it = iter(iterable)
    it >> Take(n) >> Consume()
    return it


@nut_processor
def Pick(iterable, p_n, rand=None):
    """
    iterable >> Pick(p_n)

    Pick every p_n-th element from the iterable if p_n is an integer,
    otherwise pick randomly with probability p_n.

    >>> from nutsflow import Range, Collect
    >>> from nutsflow.common import StableRandom

    >>> [1, 2, 3, 4] >> Pick(0.0) >> Collect()
    []

    >>> [1, 2, 3, 4] >> Pick(1.0) >> Collect()
    [1, 2, 3, 4]

    >>> import random as rnd
    >>> Range(10) >> Pick(0.5, StableRandom(1)) >> Collect()
    [0, 4, 5, 6, 8, 9]

    >>> [1, 2, 3, 4] >> Pick(2) >> Collect()
    [1, 3]

    :param iterable iterable: Any iterable
    :param float|int p_n: Probability p in [0, 1] or
        integer n for every n-th element
    :param Random|None rand: Random number generator. If None, random.Random()
        is used.
    :return: Iterator over picked elements.
    :rtype: iterator
    """
    rand = rnd.Random() if rand is None else rand
    if isinstance(p_n, int):
        if p_n < 0:
            raise ValueError('p_n must not be negative ' + str(p_n))
        return itt.islice(iterable, 0, None, p_n)
    if not 0 <= p_n <= 1:
        raise ValueError('Probability must be in [0, 1]: ' + str(p_n))
    return iter(e for e in iterable if rand.uniform(0, 1) <= p_n)


@nut_processor
def GroupBy(iterable, keycol=lambda x: x, nokey=False):
    """
    iterable >> GroupBy(keycol=lambda x: x, nokey=False)

    Group elements of iterable based on a column value of the element or
    the function value of keycol for the element.
    Note that elements of iterable do not need to be sorted.
    GroupBy will store all elements in memory!
    If the iterable is sorted use GroupBySorted() instead.
    see also Chunk(), ChunkWhen(), ChunkBy()

    >>> from nutsflow import Sort

    >>> [1, 2, 1, 1, 3] >> GroupBy() >> Sort()
    [(1, [1, 1, 1]), (2, [2]), (3, [3])]

    >>> [1, 2, 1, 1, 3] >> GroupBy(nokey=True) >> Sort()
    [[1, 1, 1], [2], [3]]

    >>> ['--', '+++', '**'] >> GroupBy(len) >> Sort()
    [(2, ['--', '**']), (3, ['+++'])]

    >>> ['a3', 'b2', 'c1'] >> GroupBy(1) >> Sort()
     [('1', ['c1']), ('2', ['b2']), ('3', ['a3'])]

    >>> [(1,3), (2,2), (3,1)] >> GroupBy(1, nokey=True) >> Sort()
    [[(1, 3)], [(2, 2)], [(3, 1)]]

    :param iterable iterable: Any iterable
    :param int|function keycol: Column index or key function.
    :param bool nokey: True: results will not contain keys for groups, only
        the groups themselves.
    :return: Iterator over groups.
    :rtype: iterator
    """
    isfunc = hasattr(keycol, '__call__')
    groups = cl.defaultdict(list)
    for e in iterable:
        key = keycol(e) if isfunc else e[keycol]
        groups[key].append(e)
    return six.itervalues(groups) if nokey else six.iteritems(groups)


@nut_processor
def GroupBySorted(iterable, keycol=lambda x: x, nokey=False):
    """
    iterable >> GroupBySorted(prob, keycol=lambda x: x, nokey=False)

    Group elements of iterable based on a column value of the element or
    the function value of key_or_col for the element.
    Iterable needs to be sorted according to keycol!
    See https://docs.python.org/2/library/itertools.html#itertools.groupby
    If iterable is not sorted use GroupBy but be aware that it stores all
    elements of the iterable in memory!
    see also Chunk(), ChunkWhen(), ChunkBy()

    >>> from nutsflow import Collect, nut_sink
    
    >>> @nut_sink
    ... def ViewResult(iterable):
    ...     return iterable >> Map(lambda t: (t[0], list(t[1]))) >> Collect()

    >>> [1, 1, 1, 2, 3] >> GroupBySorted() >> ViewResult()
    [(1, [1, 1, 1]), (2, [2]), (3, [3])]

    >>> [1, 1, 1, 2, 3] >> GroupBySorted(nokey=True) >> Map(list) >> Collect()
    [[1, 1, 1], [2], [3]]

    >>> ['--', '**', '+++'] >> GroupBySorted(len) >> ViewResult()
    [(2, ['--', '**']), (3, ['+++'])]

    :param iterable iterable: Any iterable
    :param int|function keycol: Column index or key function.
    :param bool nokey: True: results will not contain keys for groups, only
        the groups themselves.
    :return: Iterator over groups where values are iterators.
    :rtype: iterator
    """
    isfunc = hasattr(keycol, '__call__')
    key = keycol if isfunc else lambda x: x[keycol]
    groupiter = itt.groupby(iterable, key)
    return map(lambda k_v: k_v[1], groupiter) if nokey else groupiter


@nut_processor
def Clone(iterable, n):
    """
    iterable >> Clone(n)

    Clones elements in the iterable n times.

    >>> from nutsflow import Range, Collect, Join
    >>> Range(4) >> Clone(2) >> Collect()
    [0, 0, 1, 1, 2, 2, 3, 3]

    >>> 'abc' >> Clone(3) >> Join()
    'aaabbbccc'

    :param iterable iterable: Any iterable
    :param n: Number of clones
    :return: Generator over cloned elements in iterable
    :rtype: generator
    """
    for e in iterable:
        for _ in range(n):
            yield e


@nut_processor
def Shuffle(iterable, buffersize, rand=None):
    """
    iterable >> Shuffle(buffersize)

    Perform (partial) random shuffle of the elements in the iterable.
    Elements of the iterable are stored in a buffer of the given size
    and shuffled within. If buffersize is smaller than the length of
    the iterable the shuffle is therefore partial in the sense that the
    'window' of the shuffle is limited to buffersize.
    Note that for buffersize = 1 no shuffling occurs.

    In the following example rand = StableRandom(0) is used to create a fixed
    sequence that stable across Python version 2.x and 3.x. Usually, this is
    not what you want. Use the default rand=None which uses random.Random()
    instead.

    >>> from nutsflow import Range, Collect
    >>> from nutsflow.common import StableRandom

    >>> Range(10) >> Shuffle(5, StableRandom(0)) >> Collect()
    [4, 2, 3, 6, 7, 0, 1, 9, 5, 8]

    >>> Range(10) >> Shuffle(1, StableRandom(0)) >> Collect()
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    :param iterable iterable: Any iterable
    :param int buffersize: Number of elements stored in shuffle buffer.
    :param Random|None rand: Random number generator. If None,
           random.Random() is used.
    :return: Generator over shuffled elements
    :rtype: generator
    """
    rand = rnd.Random() if rand is None else rand
    iterable = iter(iterable)
    buffer = list(itf.take(iterable, buffersize))
    rand.shuffle(buffer)
    n = len(buffer) - 1
    for e in iterable:
        i = rand.randint(0, n)
        yield buffer[i]
        buffer[i] = e
    for e in buffer:
        yield e


@nut_processor
def MapCol(iterable, columns, func):
    """
    iterable >> MapCol(columns, func)

    Apply given function to given columns of elements in iterable.

    >>> neg = lambda x: -x
    >>> [(1, 2), (3, 4)] >> MapCol(0, neg) >> Collect()
    [(-1, 2), (-3, 4)]

    >>> [(1, 2), (3, 4)] >> MapCol(1, neg) >> Collect()
    [(1, -2), (3, -4)]

    >>> [(1, 2), (3, 4)] >> MapCol((0, 1), neg) >> Collect()
    [(-1, -2), (-3, -4)]

    :param iterable of iterables iterable: Any iterable that contains iterables
    :param int|tuple of ints columns: Column index or tuple of indexes
    :param function func: Function to apply to elements
    :return: Iterator over lists
    :rtype: iterator of list
    """
    colset = as_set(columns)
    for es in iterable:
        yield tuple(func(e) if i in colset else e for i, e in enumerate(es))


@nut_processor
def MapMulti(iterable, *funcs):
    """
    iterable >> MapMulti(*funcs)

    Map multiple functions on iterable. For each function a separate iterable
    is returned. Can consume large amounts of memory when iterables are
    processed sequentially!

    >>> from nutsflow import Collect, _
    
    >>> nums, twos, greater2 = [1, 2, 3] >> MapMulti(_, _ * 2, _ > 2)
    >>> nums >> Collect()
    [1, 2, 3]

    >>> twos >> Collect()
    [2, 4, 6]

    >>> greater2 >> Collect()
    [False, False, True]

    :param iterable iterable: Any iterable
    :param functions funcs: Functions to map
    :return: Iterators for each function
    :rtype: (iterator, ...)
    """
    tees = itt.tee(iterable, len(funcs))
    return [map(f, t) for f, t in zip(funcs, tees)]


# Don't use @nut_processor here. Creating Pool is expensive!
# ParMap is of limited use since 'func' must be pickable many objects are not :(
# pathos.multiprocesssing might be an alternative
class MapPar(Nut):
    def __init__(self, func, chunksize=mp.cpu_count()):
        """
        iterable >> MapPar(func, chunksize=mp.cpu_count())

        Map function in parallel. Order of iterable is preserved.
        Note that ParMap is of limited use since 'func' must be pickable
        and only top level functions (not class methods) are pickable. See
        https://docs.python.org/2/library/pickle.html

        >>> from nutsflow import Collect
        >>> [-1, -2, -3] >> MapPar(abs) >> Collect()
        [1, 2, 3]

        :param iterable iterable: Any iterable
        :param function func: Function to map
        :param int chunksize: Number of parallel processes to use for mapping.
        :return: Iterator over mapped elements
        :rtype: iterator
        """
        self.pool = mp.Pool(processes=mp.cpu_count())
        self.func = func
        self.chunksize = chunksize

    def __rrshift__(self, iterable):
        it = iter(iterable)
        results = 1
        while results:
            sliced = itt.islice(it, self.chunksize)
            results = self.pool.map(self.func, sliced)
            for r in results:
                yield r


class Cache(Nut):
    """
    A very naive implementation of a disk cache. Pickles elements of iterable
    to file system and loads them the next time instead of recomputing.
    """

    def __init__(self, cachepath=None, clearcache=True):
        """
        iterable >> Cache()

        Cache elements of iterable to disk. Only worth it if elements of
        iterable are time-consuming to produce and can be loaded faster
        from disk.

        .. code:: python

            with Cache() as cache:
                data = range(100)
                for i in range(10):
                    data >> expensive_op >> cache >> process(i) >> Consume()


        .. code:: python

            cache = Cache()
            for _ in range(100)
                data >> expensive_op >> cache >> Collect()
            cache.clear()


        .. code:: python

            with Cache('path/to/mycache') as cache:
                for _ in range(100)
                    data >> expensive_op >> cache >> Collect()

        :param iterable iterable: Any iterable
        :param string cachepath: Path to a folder that stores the cached
           objects. If the path does not exist it will be created. The path
           with all its contents will be deleted when the cache is deleted.
           For cachepath=None a temporary folder will be created. Path to
           this folder is available in cache.path.
        :param bool clearcache: Clear left-over cache if it exists.
        :return: Iterator over elements
        :rtype: iterator
        """
        self.path = None
        self._cachepath = cachepath
        self._clearcache = clearcache
        if clearcache and cachepath and os.path.exists(cachepath):
            shutil.rmtree(cachepath)  # delete it.

    def clear(self):
        """Clear cache"""
        shutil.rmtree(self.path, ignore_errors=True)
        self.path = None

    def _fpath(self, idx):
        """
        Return filepath for object to cache for the given index.
        :param int idx: Index of object in iterable
        :return: Filepath to pickle file
        :rtype: str
        """
        fname = 'cache_{0:010d}.pkl'.format(idx)
        return osp.join(self.path, fname)

    def _cache_fpaths(self):
        """
        Return sorted list of filepaths of cached objects.

        :return: Filepaths to pickle files.
        :rtype: list of strings
        """
        path = self._cachepath if self._cachepath else self.path
        return sorted(osp.join(path, n) for n in os.listdir(path))

    def _create_cache(self):
        """
        Create either user-defined cache path or temporary path for cache data.
        """
        if self._cachepath:  # user defined cache path.
            if not os.path.exists(self._cachepath):
                os.makedirs(self._cachepath)  # create cache
        self.path = self._cachepath if self._cachepath else tempfile.mkdtemp()

    def __enter__(self):
        """
        Context manager API to support 'with' statement.

        :return: Cache itself.
        :rtype: Cache
        """
        return self

    def __exit__(self, *args):
        """
        Context manager API. Clears the cache when exiting 'with' statement.
        """
        self.clear()

    def __iter__(self):
        """
        Return iterator over cached elements.

        :return: Generator over cached elements
        :rtype: Generator
        """
        for fpath in self._cache_fpaths():
            with open(fpath, 'rb') as f:
                yield pickle.load(f)

    def __rrshift__(self, iterable):
        """
        Return elements in iterable.

        :param iterable iterable: Any iterable
        :return: Generator over same elements as input iterable.
        :rtype: Generator
        """
        if self.path or (self._cachepath and not self._clearcache):
            for e in self.__iter__():
                yield e
        else:
            self._create_cache()
            for i, e in enumerate(iterable):
                with open(self._fpath(i), 'wb') as f:
                    pickle.dump(e, f, pickle.HIGHEST_PROTOCOL)
                yield e


@nut_processor
def Prefetch(iterable, num_prefetch=1):
    """
    iterable >> Prefetch(num_prefetch=1)

    Prefetch elements from iterable.
    Typically used to keep the CPU busy while the GPU is crunching.

    >>> from nutsflow import Take, Consume
    >>> it = iter([1, 2, 3, 4])
    >>> it >> Prefetch(1) >> Take(1) >> Consume()
    >>> next(it)   # doctest: +SKIP
    3

    :param iterable iterable: Any iterable
    :param int num_prefetch: Number of elements to prefetch.
    :return: Iterator over input elements
    :rtype: iterator
    """
    return itf.PrefetchIterator(iterable, num_prefetch)


class PrintProgress(Nut):
    def __init__(self, data, title='progress:', every_sec=10.0):
        """
        iterable >> PrintProgress(data, every_sec=10.0)

        Print progress on iterable. Requires that length of iterable is known
        beforehand. Data are just passed through.
        For long running computations and Estimated time of arrival (eta) is
        printed as well

        range(10) >> PrintProgress(10, 'numbers:', 0) >> Consume()

        :param iterable iterable: Any iterable
        :param int data: Number of elements in iterable or realized iterable.
               If data is provided it must not be an iterator since it will be
               consumed!
        :param str title: Title of progress print out (prefix text)
        :param float every_sec: Progress is printed every 'every_sec' seconds.

        :return: Iterator over input elements
        :rtype: iterator
        """
        self.n = (data if isinstance(data, int) else len(data)) - 1
        self.title = title
        self.every_sec = every_sec

    def __rrshift__(self, iterable):
        etafmt = '(eta: {:d}:{:02d}:{:02d})'
        endfmt = '(took: {:d}:{:02d}:{:02d})'
        start_time = time.time()
        up_time = time.time()
        for i, e in enumerate(iterable):
            if (time.time() - up_time) >= self.every_sec:
                up_time = time.time()
                per_done = int(100 * i / self.n)
                sec_consumed = int(time.time() - start_time)
                eta = sec_consumed * (self.n / float(i) - 1) if i else 0
                tstr = timestr(eta, etafmt)
                text = '\r{} {}% {}'.format(self.title, per_done, tstr)
                console(text, end='')
            yield e
        duration = int(time.time() - start_time)
        text = '\r{} 100% {}'.format(self.title, timestr(duration, endfmt))
        console(text)


@nut_processor
def Try(iterable, func, default='STDERR'):
    """
    iterable >> Try(nut)

    Exception handling for (nut) functions. If the wrapped nut or function 
    raises an exception it is caught and handled with the provided handler.
    Per default the exception and the value causing it are printed.
    Furthermore a default value can be specified that is returned instead
    of the nut output if an exception occurs. Per default no output is
    returned but an error message printed (STDERR).

    NOTE: In the following examples 'STDOUT' is used only to verify the
    error message within the doctest. In production code use the default
    value of 'STDERR'.

    >>> from nutsflow import Try, Collect, nut_function  

    >>> [10, 2, 1] >> Try(lambda x : 10//x) >> Collect()
    [1, 5, 10]
    >>> [10, 0, 1] >> Try(lambda x : 10//x, 'STDOUT') >> Collect()
    ERROR: 0 : integer division or modulo by zero
    [1, 10]

    >>> Div = nut_function(lambda x : 10//x)
    >>> [10, 2, 1] >> Try(Div()) >> Collect()
    [1, 5, 10]
    >>> [10, 0, 1] >> Try(Div(), 'STDOUT') >> Collect()
    ERROR: 0 : integer division or modulo by zero
    [1, 10]
    >>> [10, 0, 1] >> Try(Div(), -1) >> Collect()
    [1, -1, 10]

    >>> handlezero = lambda x, e: 'FAILED: '+str(x)
    >>> [10, 0, 1] >> Try(Div(), handlezero) >> Collect()
    [1, 'FAILED: 0', 10]

    >>> handlezero = lambda x, e: str(e)
    >>> [10, 0, 1] >> Try(Div(), handlezero) >> Collect()
    [1, 'integer division or modulo by zero', 10]

    :param iterable iterable: Iterable the nut operates on.
    :param function|NutFunction func: (Nut) function that is wrapped 
       for exception handling. Can be a plain Python function/method as well.
    :param Object default: Return value if exception occurs. 
       If default = 'IGNORE', no value is returned and no error is printed.
       If default = 'STDERR', no value is returned, error is printed to stderr.
       If default = 'STDOUT', no value is returned, error is printed to stdout.
       If default is function that takes element x and  exception e
          as parameters its result is returned and no error is printed.
       Otherwise the default value is returned and no error is printed.
    :return: Iterator over input elements transformed by provided nut.
    :rtype: iterator
    """
    if not (isinstance(func, NutFunction) or isfunction(func) or
                isbuiltin(func) or ismethod(func)):
        raise TypeError('Need (nut) function in Try() :' + str(func))
    for x in iterable:
        try:
            yield func(x)
        except Exception as e:
            if default == 'IGNORE':
                pass
            elif default == 'STDERR':
                print('ERROR:', x, ':', e, file=sys.stderr)
            elif default == 'STDOUT':
                print('ERROR:', x, ':', e)
            elif hasattr(default, '__call__'):
                yield default(x, e)
            else:
                yield default
