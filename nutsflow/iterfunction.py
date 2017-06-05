"""
.. module:: iterfunction
   :synopsis: Functions that work with iterables.
              See https://docs.python.org/2/library/itertools.html
"""
import six

import itertools as itt
import threading as t
import collections as cl

from six.moves import queue as q
from six import advance_iterator
from six.moves import map, filter, filterfalse


def length(iterable):
    """
    Return number of elements in iterable. Consumes iterable!

    >>> length(range(10))
    10

    :param iterable iterable: Any iterable, e.g. list, range, ...
    :return: Length of iterable.
    :rtype: int
    """
    return sum(1 for _ in iterable)


def interleave(*iterables):
    """
    Return generator that interleaves the elements of the iterables.

    >>> list(interleave(range(5), 'abc'))
    [0, 'a', 1, 'b', 2, 'c', 3, 4]

    >>> list(interleave('12', 'abc', '+-'))
    ['1', 'a', '+', '2', 'b', '-', 'c']

    :param iterable iterables: Collection of iterables, e.g. lists, range, ...
    :return: Interleaved iterables.
    :rtype: iterator
    """
    pending = len(iterables)
    fnext = lambda it: lambda: advance_iterator(it)
    nexts = itt.cycle(fnext(iter(it)) for it in iterables)
    while pending:
        try:
            for nxt in nexts:
                yield nxt()
        except StopIteration:
            pending -= 1
            nexts = itt.cycle(itt.islice(nexts, pending))


def take(iterable, n):
    """
    Return iterator over last n elements of given iterable.

    >>> list(take(range(10), 3))
    [0, 1, 2]

    See: https://docs.python.org/2/library/itertools.html#itertools.islice

    :param iterable iterable: Any iterable, e.g. list, range, ...
    :param int n: Number of elements to take
    :return: Iterator over last n elements
    :rtype: iterator
    """
    return itt.islice(iterable, n)


def nth(iterable, n, default=None):
    """
    Return n-th element of iterable. Consumes iterable!

    >>> nth(range(10), 2)
    2

    >>> nth(range(10), 100, default=-1)
    -1

    https://docs.python.org/2/library/itertools.html#itertools.islice

    :param iterable iterable: Any iterable, e.g. list, range, ...
    :param n: Index of element to retrieve.
    :param default: Value to return when iterator is depleted
    :return: nth element
    :rtype: Any or default value.
    """
    return next(itt.islice(iterable, n, None), default)


def unique(iterable, key=None):
    """
    Return only unique elements in iterable. Potentially high mem. consumption!

    >>> list(unique([2,3,1,1,2,4]))
    [2, 3, 1, 4]

    >>> ''.join(unique('this is a test'))
    'this ae'

    >>> data = [(1,'a'), (2,'a'), (3,'b')]
    >>> list(unique(data, key=lambda t: t[1]))
    [(1, 'a'), (3, 'b')]

    :param iterable iterable: Any iterable, e.g. list, range, ...
    :param key: Function used to compare for equality.
    :return: Iterator over unique elements.
    :rtype: Iterator
    """
    seen = set()
    for e in iterable:
        k = key(e) if key else e
        if k not in seen:
            seen.add(k)
            yield e


def chunked(iterable, n):
    """
    Split iterable in chunks of size n, where each chunk is also an iterator.

    for chunk in chunked(range(10), 3):
        for element in chunk:
            print element

    >>> it = chunked(range(7), 2)
    >>> list(map(tuple, it))
    [(0, 1), (2, 3), (4, 5), (6,)]

    :param iterable iterable: Any iterable, e.g. list, range, ...
    :param n: Chunk size
    :return: Chunked iterable
    :rtype: Iterator over iterators
    """
    it = iter(iterable)
    while True:
        chunk_it = itt.islice(it, n)
        try:
            first_el = next(chunk_it)
        except StopIteration:
            return
        yield itt.chain((first_el,), chunk_it)


def consume(iterable, n=None):
    """
    Consume n elements of the iterable.

    >>> it = iter([1,2,3,4])
    >>> consume(it, 2)
    >>> next(it)
    3

    See https://docs.python.org/2/library/itertools.html

    :param iterable iterable: Any iterable, e.g. list, range, ...
    :param n: Number of elements to consume. For n=None all are consumed.
    """
    if n is None:
        cl.deque(iterable, maxlen=0)
    else:
        next(itt.islice(iterable, n, n), None)


def flatten(iterable):
    """
    Return flattened iterable.

    >>> list(flatten([(1,2), (3,4,5)]))
    [1, 2, 3, 4, 5]

    :param iterable iterable:
    :return: Iterator over flattened elements of iterable
    :rtype: Iterator
    """
    return itt.chain(*iterable)


def flatmap(func, iterable):
    """
    Map function to iterable and flatten.

    >>> f = lambda n: str(n) * n
    >>> list( flatmap(f, [1, 2, 3]) )
    ['1', '2', '2', '3', '3', '3']

    >>> list( map(f, [1, 2, 3]) )  # map instead of flatmap
    ['1', '22', '333']

    :param function func: Function to map on iterable.
    :param iterable iterable: Any iterable, e.g. list, range, ...
    :return: Iterator of iterable elements transformed via func and flattened.
    :rtype: Iterator
    """
    return itt.chain.from_iterable(map(func, iterable))


def partition(iterable, pred):
    """
    Split iterable into two partitions based on predicate function

    >>> pred = lambda x: x < 6
    >>> smaller, larger = partition(range(10), pred)
    >>> list(smaller)
    [0, 1, 2, 3, 4, 5]

    >>> list(larger)
    [6, 7, 8, 9]

    :param iterable: Any iterable, e.g. list, range, ...
    :param pred: Predicate function.
    :return: Partition iterators
    :rtype: Two iterators
    """
    t1, t2 = itt.tee(iterable)
    return filter(pred, t1), filterfalse(pred, t2)


class PrefetchIterator(t.Thread, six.Iterator):
    """
    Wrap an iterable in an iterator that prefetches elements.

    Typically used to fetch samples or batches while the the GPU processes
    the batch. Keeps the CPU busy pre-processing data and not waiting for the
    GPU to finish the batch.

    >>> from __future__ import print_function
    >>> for i in PrefetchIterator(range(4)):
    ...    print(i)
    0
    1
    2
    3
    """

    def __init__(self, iterable, num_prefetch=1):
        """
        Constructor.

        :param iterable iterable: Iterable elements are fetched from.
        :param int num_prefetch: Number of elements to pre-fetch.
        """
        t.Thread.__init__(self)
        self.queue = q.Queue(num_prefetch)
        self.iterable = iterable
        self.daemon = True
        self.start()

    def run(self):
        """
        Put elements in input iterable into queue.
        """
        for item in self.iterable:
            self.queue.put(item)
        self.queue.put(None)

    def __next__(self):
        """
        Return next element from pre-fetch iterator.

        :return: element from iterator
        :rtype: same as element type of input iterable.
        """
        next_item = self.queue.get()
        if next_item is None:
            raise StopIteration
        return next_item

    def __iter__(self):
        """
        Return pre-fetch iterator

        :return: pre-fetch iterator
        :rtype: PrefetchIterator
        """
        return self
