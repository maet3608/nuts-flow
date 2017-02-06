"""
.. module:: processor
   :synopsis: Nuts that process iterables and return iterables.
"""

import tempfile
import shutil
import os
import time

import cPickle as pickle
import os.path as osp
import itertools as itt
import iterfunction as itf
import random as rnd
import multiprocessing as mp
import collections as cl

from base import Nut
from factory import nut_processor
from function import Identity
from sink import Consume, Collect
from nutsflow.common import etastr

Take = nut_processor(itf.take)
"""
iterable >> Take(n)

Return first n elements of iterable

>>> [1, 2, 3, 4] >> Take(2) >> Collect()
[1, 2]

:param iterable iterable: Any iterable
:param int n: Number of elements to take
:return: First n elements of iterable
:rtype: iterator
"""

Slice = nut_processor(itt.islice)
"""
iterable >> Slice(start, stop[, step])

Return slice of elements from iterable.
See https://docs.python.org/2/library/itertools.html#itertools.islice

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

Interleave = nut_processor(itf.interleave)
"""
iterable >> Interleave(*iterables)

Interleave elements of iterable with elements of given iterables.
Similar to iterable >> Zip(*iterables) >> Flatten() but longest iterable
determines length of interleaved iterator.

>>> Range(5) >> Interleave('abc') >> Collect()
[0, 'a', 1, 'b', 2, 'c', 3, 4]

>>> '12' >> Interleave('abcd', '+-') >> Collect()
['1', 'a', '+', '2', 'b', '-', 'c', 'd']


:param iterable iterable: Any iterable
:param iterable iterables: Iterables to interleave
:return: Interleaved elements from iterables.
:rtype: iterator
"""

Zip = nut_processor(itt.izip)
"""
iterable >> Zip(*iterables)

Zip elements of iterable with elements of given iterables
Zip finishes when shortest iterable is exhausted.
See https://docs.python.org/2/library/itertools.html#itertools.izip
And https://docs.python.org/2/library/itertools.html#itertools.izip_longest

>>> [0, 1, 2] >> Zip('abc') >> Collect()
[(0, 'a'), (1, 'b'), (2, 'c')]

>>> '12' >> Zip('abcd', '+-') >> Collect()
[('1', 'a', '+'), ('2', 'b', '-')]


:param iterable iterable: Any iterable
:param iterable iterables: Iterables to interleave
:return: Interleaved elements from iterables.
:rtype: iterator
"""

Unique = nut_processor(itf.unique)
"""
iterable >> Unique([key])

Return only unique elements in iterable. Can have very high memory consumption
if iterable is long and many elements are unique!

>>> [2,3,1,1,2,4] >> Unique() >> Collect()
[2, 3, 1, 4]

>>> data = [(1,'a'), (2,'a'), (3,'b')]
>>> data >> Unique(key=lambda (x,y): y) >> Collect()
[(1, 'a'), (3, 'b')]

>> data >> Unique(_[1]) >> Collect()
[(1, 'a'), (3, 'b')]

:param iterable iterable: Any iterable, e.g. list, xrange, ...
:param key: Function used to compare for equality.
:return: Iterator over unique elements.
:rtype: Iterator
"""

Chunked = nut_processor(itf.chunked)
"""
iterable >> Chunked(n)

Split iterable in chunks of size n, where each chunk is also an iterator.

>>> for chunk in Range(5) >> Chunked(2):
>>> ... print list(chunk)
[0, 1]
[2, 3]
[4]

:param iterable iterable: Any iterable, e.g. list, xrange, ...
:param n: Chunk size
:return: Chunked iterable
:rtype: Iterator over iterators
"""

Cycle = nut_processor(itt.cycle)
"""
iterable >> Cycle()

Cycle through iterable indefinitely. Large memory consumption if iterable is
large!

>>> [1,2] >> Cycle() >> Take(5) >> Collect()
[1, 2, 1, 2, 1]

:param iterable iterable: Any iterable, e.g. list, xrange, ...
:param n: Chunk size
:return: Chunked iterable
:rtype: Iterator over iterators
"""

Flatten = nut_processor(itt.chain.from_iterable)
"""
iterable >> Flatten()

Flatten the iterables within the iterable. Only one level deep flattening.
See https://docs.python.org/2/library/itertools.html#itertools.chain.from_iterable

>>> [(1,2), (3,4,5)] >> Flatten() >> Collect()
[1, 2, 3, 4, 5]

:param iterable iterable: Any iterable that contains iterables.
:return: Flattened iterable
:rtype: Iterator
"""

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

Map = nut_processor(itt.imap, 1)
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
:param iterable iterables: Any iterable.
:param function func: Mapping function.
:return: Mapped iterable
:rtype: Iterator
"""

Filter = nut_processor(itt.ifilter, None)
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

FilterFalse = nut_processor(itt.ifilterfalse, None)
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

Partition = nut_processor(itf.partition)
"""
partition1, partition2 = iterable >> Partition(func)

Split iterable into two partitions based on predicate function

>>> smaller, larger = Range(5) >> Partition(_ < 3)
>>> smaller >> Collect()
[0, 1, 2]
>>> larger >> Collect()
[3, 4]

:param iterable: Any iterable, e.g. list, xrange, ...
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
:return: Iterable
:rtype: Iterator
"""

Combine = nut_processor(itt.combinations)
"""
iterable >> Combine(r)

Return r length subsequences of elements from the input iterable.
See https://docs.python.org/2/library/itertools.html#itertools.combinations

>>> 'ABC' >> Combine(2) >> Collect()
[('A', 'B'), ('A', 'C'), ('B', 'C')]

:param iterable iterable: Any iterable
:param int r: Length of combinations
:return: Iterable
:rtype: Iterator
"""

Tee = nut_processor(itt.tee)
"""
iterable >> Tee([n=2])

Return n independent iterators from a single iterable. Can consume large
amounts of memory if iterable is large and tee's are not processed in
parallel.
See https://docs.python.org/2/library/itertools.html#itertools.tee

>>> it1, it2  = [1, 2, 3] >> Tee(2) >> Collect()
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
def Skip(iterable, n):
    """
    iterable >> Skip(n)

    Skip n elements in iterable.

    >>> [1, 2, 3, 4] >> Skip(2) >> Collect()
    [3, 4]


    :param iterable iterable: Any iterable
    :param int n: Number of elements to skip
    :return: Iterator without skipped elements
    :rtype: iterator
    """
    it = iter(iterable)
    it >> Take(n) >> Consume()
    return it


@nut_processor
def Choice(iterable, prob):
    """
    iterable >> Choice(prob)

    Randomly sample elements from iterable with given probability.
    Sampling is with no replacement.

    >>> [1, 2, 3] >> Choice(0.0) >> Collect()
    []

    >>> [1, 2, 3] >> Choice(1.0) >> Collect()
    [1, 2, 3]

    :param iterable iterable: Any iterable
    :param float prob: Probability [0,1]
    :return: Iterator over randomly sampled elements.
    :rtype: iterator
    """
    if not 0 <= prob <= 1:
        raise ValueError('Probability must be in [0,1]: ' + str(prob))
    for e in iterable:
        if rnd.random() <= prob:
            yield e


@nut_processor
def GroupBy(iterable, keycol=lambda x: x, nokey=False):
    """
    iterable >> GroupBy(prob, keycol=lambda x: x, nokey=False)

    Group elements of iterable based on a column value of the element or
    the function value of keycol for the element.
    Note that elements of iterable do not need to be sorted.
    GroupBy will store all elements in memory!
    If the iterable is sorted use GroupBySorted() instead.

    >>> [1, 2, 1, 1, 3] >> GroupBy() >> Collect()
    [(1, [1, 1, 1]), (2, [2]), (3, [3])]

    >>> [1, 2, 1, 1, 3] >> GroupBy(nokey=True) >> Collect()
    [[1, 1, 1], [2], [3]]

    >>> ['--', '+++', '**'] >> GroupBy(len) >> Collect()
    [(2, ['--', '**']), (3, ['+++'])]

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
    return groups.itervalues() if nokey else groups.iteritems()


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

    >>> @nut_sink
    ... def ViewResult(iterable):
    ...     return iterable >> Map(lambda (k, es): (k, list(es))) >> Collect()

    >>> [1,1, 1, 2, 3] >> GroupBySorted() >> ViewResult()
    [(1, [1, 1, 1]), (2, [2]), (3, [3])]

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
    return itt.imap(lambda (k,v): v, groupiter) if nokey else groupiter


@nut_processor
def Shuffle(iterable, buffersize, rand=rnd.Random()):
    """
    iterable >> Shuffle(buffersize)

    Perform (partial) random shuffle of the elements in the iterable.
    Elements of the iterable are stored in a buffer of the given size
    and shuffled within. If buffersize is smaller than the length of
    the iterable the shuffle is therefore partial in the sense that the
    'window' of the shuffle is limited to buffersize.
    Note that for buffersize = 1 no shuffling occurs.

    In the following example rand = rnd.Random(0) is used to create a fixed
    shuffle. Usually, this is not what you want. Use the default
    rand=rnd.Random() instead.

    >>> Range(10) >> Shuffle(5, rnd.Random(0)) >> Collect()
    [1, 5, 3, 0, 6, 2, 8, 9, 7, 4]

    >>> Range(10) >> Shuffle(1, rnd.Random(0)) >> Collect()
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    :param iterable iterable: Any iterable
    :param int buffersize: Number of elements stored in shuffle buffer.
    :param random.Random rand: Random number generator.
    :return: Iterator over shuffled elements
    :rtype: iterator
    """
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
def ColMap(iterable, columns, func):
    """
    iterable >> ColMap(columns, func)

    Apply given function to given columns of elements in iterable.

    >>> neg = lambda x: -x
    >>> [(1, 2), (3, 4)] >> ColMap(0, neg) >> Collect()
    [[-1, 2], [-3, 4]]

    >>> [(1, 2), (3, 4)] >> ColMap(1, neg) >> Collect()
    [[1, -2], [3, -4]]

    >>> [(1, 2), (3, 4)] >> ColMap((0, 1), neg) >> Collect()
    [[-1, -2], [-3, -4]]

    :param iterable of iterables iterable: Any iterable that contains iterables
    :param int|tuple of ints columns: Column index or tuple of indexes
    :param function func: Function to apply to elements
    :return: Iterator over lists
    :rtype: iterator of list
    """
    colset = {columns} if isinstance(columns, int) else set(columns)
    for elements in iterable:
        yield [func(e) if i in colset else e for i, e in enumerate(elements)]


@nut_processor
def MultiMap(iterable, *funcs):
    """
    iterable >> MultiMap(*funcs)

    Map multiple functions on iterable. For each function a separate iterable
    is returned. Can consume large amounts of memory when iterables are
    processed sequentially!

    >>> nums, twos, greater2 = [1, 2, 3] >> MultiMap(_, _ * 2, _ > 2)
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
    return [itt.imap(f, t) for f, t in zip(funcs, tees)]


# Don't use @nut_processor here. Creating Pool is expensive!
# ParMap is of limited use since 'func' must be pickable many objects are not :(
# pathos.multiprocesssing might be an alternative
class ParMap(Nut):
    def __init__(self, func, chunksize=mp.cpu_count()):
        """
        iterable >> ParMap(func, chunksize=mp.cpu_count())

        Map function in parallel. Order of iterable is preserved.
        Note that ParMap is of limited use since 'func' must be pickable
        and only top level functions (not class methods) are pickable. See
        https://docs.python.org/2/library/pickle.html

        >>> from nutsflow import Collect
        >>> [-1, -2, -3] >> ParMap(abs) >> Collect()
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
    to file system and loads them the next time istead of recomputing.
    """

    def __init__(self, storage='disk'):
        """
        iterable >> Cache()

        Cache elements of iterable to disk. Only worth it if elements of
        iterable are time-consuming to produce and can be loaded faster
        from disk.

        .. code:: python

            with Cache() as cache:
                data = xrange(100)
                for i in xrange(10):
                    data >> expensive_op >> cache >> process(i) >> Consume()


         .. code:: python

            cache = Cache()
                for _ in xrange(100)
                    data >> expensive_op >> cache >> Collect()
                cache.clear()

        :param iterable iterable: Any iterable
        :param string storage: Currently only 'disk' mode.
        :return: Iterator over elements
        :rtype: iterator
        """

        self._dirpath = None
        self.storage = storage  # currently not used. Could be 'disk', 'memory'
        if storage != 'disk':
            raise ValueError('Unsupported storage: ' + storage)

    def clear(self):
        """Clear cache"""
        shutil.rmtree(self._dirpath, ignore_errors=True)
        self._dirpath = None

    def _fpath(self, idx):
        """
        Return filepath for object to cache for the given index.
        :param int idx: Index of object in iterable
        :return: Filepath to pickle file
        :rtype: str
        """
        fname = 'cache_{0:010d}.pkl'.format(idx)
        fpath = osp.join(self._dirpath, fname)
        return fpath

    def _cache_fpaths(self):
        """
        Return sorted list of filepaths of cached objects.

        :return: Filepaths to pickle files.
        :rtype: list of strings
        """
        dirpath = self._dirpath
        return sorted(osp.join(dirpath, name) for name in os.listdir(dirpath))

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

    def __rrshift__(self, iterable):
        """
        Return elements in iterable.

        :param iterable iterable: Any iterable
        :return: Iterable over same elements as input iterable.
        :rtype: iterable
        """
        if self._dirpath:
            for fpath in self._cache_fpaths():
                with open(fpath, 'rb') as f:
                    yield pickle.load(f)
        else:
            self._dirpath = tempfile.mkdtemp()
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

    >>> it = iter([1, 2, 3, 4])
    >>> it >> Prefetch() >> Take(1) >> Collect()
    [1]
    >>> next(it)
    3

    :param iterable iterable: Any iterable
    :param int num_prefetch: Number of elements to prefetch.
    :return: Iterator over input elements
    :rtype: iterator
    """
    return itf.PrefetchIterator(iterable, num_prefetch)


class PrintProgress(Nut):
    def __init__(self, data, update=10.0):
        """
        iterable >> PrintProgress(data, update=10.0)

        Print progress on iterable. Requires that length of iterable is known
        beforehand. Data are just passed through.
        For long running computations and Estimated time of arrival (eta) is
        printed as well

        xrange(10) >> PrintProgress(numbers, 0) >> Consume()

        :param iterable iterable: Any iterable
        :param int data: Number of elements in iterable or realized iterable.
               If data is provided it must not be an iterator since it will be
               consumed!
        :param float update: Progress is printed every 'update' seconds.
        :return: Iterator over input elements
        :rtype: iterator
        """
        self.n = (data if isinstance(data, int) else len(data)) - 1
        self.update = update

    def __rrshift__(self, iterable):
        start_time = time.clock()
        up_time = time.clock()
        for i, e in enumerate(iterable):
            if (time.clock() - up_time) >= self.update:
                up_time = time.clock()
                per_done = 100 * i / self.n
                sec_consumed = int(time.clock() - start_time)
                eta = sec_consumed * (self.n / float(i) - 1) if i else 0
                print '\rprogress: %d%% %s' % (per_done, etastr(eta)),
            yield e
        print
