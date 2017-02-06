"""
.. module:: sink
   :synopsis: Nuts that reads streams and potentially produce non-stream output.
"""

import csv

import itertools as itt
import collections as cl

from base import NutSink
from factory import nut_sink
from iterfunction import nth, consume, length, take

Sum = nut_sink(sum)
"""
iterable >> Sum()

Return sum over inputs.

>>> [1, 2, 3] >> Sum()
6

:param iterable iterable: Iterable over numbers
:return: Sum of numbers
:rtype: number
"""

Reduce = nut_sink(reduce, 1)
"""
iterable >> Reduce(func [,initiaizer])

Reduces the iterable using the given function.
See https://docs.python.org/2/library/functions.html#reduce

>>> [1, 2, 3] >> Reduce(lambda a,b: a+b)
6

>>> [2] >> Reduce(lambda a,b: a*b, 1)
2

:param iterable iterable: Iterable
:param function func: Reduction function
:return: Result of reduction
:rtype: any
"""

Nth = nut_sink(nth)
"""
iterable >> Nth(nth)

Return n-th element of iterable. This consumes the iterable!

>>> 'test' >> Nth(2)
s

:param iterable iterable: Iterable
:param int nth: Index of element in iterable to return
:return: n-th element
:rtype: any
"""

Consume = nut_sink(consume)
"""
iterable >> Consume(n=None)

Consume n elements of the iterable.

>>> [1,2,3] >> Print() >> Consume()   # Without Consume nothing happens!
1
2
3

>>> [1,2,3] >> Print() >> Consume(2)
1
2

:param iterable iterable: Iterable
:param int n: Number of elements to consume.
              n = None means the whole iterable is consumed.

"""

Len = nut_sink(length)
"""
iterable >> Len()

Return length of input iterable.  This consumes the iterable!

>>> [0, 1, 2] >> Len()
3

:param iterable iterable: Iterable
:return: Number elements in interable
:rtype: int
"""


@nut_sink
def Unzip(iterable, noiter=False):
    """
    iterable >> Unzip()

    Same as zip(*iterable) but returns iterators for noiter=False.

    >>> [(1, 2, 3), (4, 5, 6)] >> Unzip() >> Map(tuple) >> Collect()
    [(1, 4), (2, 5), (3, 6)]

    :param iterable iterable:  Any iterable, e.g. list, xrange, ...
    :param bool noiter:  If true, does not return iterator
    :return: Unzip iterable.
    :rtype: iterator over iterators
    """
    return zip(*iterable) if noiter else itt.izip(*iterable)


@nut_sink
def Head(iterable, n, container=list):
    """
    iterable >> Head(n, container=list)

    Collect first n elements of iterable in specified container.

    >>> [1, 2, 3, 4] >> Head(2)
    [1, 2]

    :param iterable iterable: Any iterable, e.g. list, xrange, ...
    :param int n: Number of elements to take.
    :param container container: Container to collect elements in, e.g. list, set
    :return: Container with head elements
    :rtype: container
    """
    return container(take(iterable, n))


@nut_sink
def Tail(iterable, n, container=list):
    """
    iterable >> Tail(n, container=list)

    Collect last n elements of iterable in specified container. This consumes
    the iterable completely!

    >>> [1, 2, 3, 4] >> Tail(2)
    [1, 2]

    :param iterable iterable: Any iterable, e.g. list, xrange, ...
    :param int n: Number of elements to take.
    :param container container: Container to collect elements in, e.g. list, set
    :return: Container with tail elements
    :rtype: container
    """
    return container(cl.deque(iterable, n))


@nut_sink
def Counts(iterable):
    """
    iterable >> Counts()

    Return dictionary with counts of the elements in the input iterable.

    >>> 'abaacc' >> Counts()
    {'a':3, 'b':1, 'c':2}

    :param iterable iterable: Any iterable, e.g. list, xrange, ...
    :return: Dictionary with counts for elements in iterable.
    :rtype: dict
    """
    return dict(cl.Counter(iterable))


@nut_sink
def Frequencies(iterable):
    """
    iterable >> Frequencies()

    Return dictionary with frequencies of the elements in the input iterable.

    >>> 'aabaab' >> Frequencies()
    {'a': 1.0, 'b': 0.5}

    :param iterable iterable: Any iterable, e.g. list, xrange, ...
    :return: Dictionary with frequencies for elements in iterable.
    :rtype: dict
    """
    cnts = dict(cl.Counter(iterable))
    if not cnts.values():
        return dict()
    max_cnt = max(cnts.values())
    n = float(max_cnt) if max_cnt else 1.0
    return {k: v / n for k, v in cnts.iteritems()}


@nut_sink
def Collect(iterable, container=list):
    """
    iterable >> Collect(container)

    Collects all elements of the iterable input in the given container.

    >>> xrange(5) >> Collect()
    [0, 1, 2, 3, 4]

    >>> [1, 2, 3, 2] >> Collect(set)
    set([1,2,3])

    >>> [('one', 1), ('two',2)] >> Collect(dict)
    {'one':1, 'two':2}

    :param iterable iterable: Any iterable, e.g. list, xrange, ...
    :param container container: Some container, e.g. list, set, dict
           that can be filled from an iterable
    :return: Container
    :rtype: container
    """
    return container(iterable)


class WriteCSV(NutSink):
    """
    Write data to a CSV file using Python's CSV writer.
    See: https://docs.python.org/2/library/csv.html
    """

    def __init__(self, filepath, columns=None, skipheader=0,
                 fmtfunc=lambda x: x, **kwargs):
        """
        CSVWriter(filepath, columns, skipheader, fmtfunc, **kwargs)

        Write data in Comma Separated Values format (CSV) and other formats
        to file. Tab Separated Values (TSV) files can be written by
        specifying a different delimiter. Note that in the docstring below
        delimiter is '\\t' but in code it should be '\t'. See unit tests.

        Also see https://docs.python.org/2/library/csv.html
        and CSVReader.


        >>> import os
        >>> filepath = 'tests/data/temp_out.csv'
        >>> with WriteCSV(filepath) as writer:
        ...     xrange(10) >> writer
        >>> os.remove(filepath)

        >>> with WriteCSV(filepath, columns=(1,0)) as writer:
        ...     [(1,2), (3,4)] >> writer
        >>> os.remove(filepath)

        >>> filepath = 'tests/data/temp_out.tsv'
        >>> with WriteCSV(filepath, delimiter='\\t') as writer:
        ...     [[1,2], [3,4]] >> writer
        >>> os.remove(filepath)


        :param string filepath: Path to file in CSV format.
        :param tuple columns: Indices of the columns to write.
                              If None all columns are written.
        :param int skipheader: Number of header rows to skip.
        :param function fmtfunc: Function to apply to the elements of each row.
        :param kwargs kwargs: Keyword arguments for Python's CSV writer.
                              See https://docs.python.org/2/library/csv.html
        """
        self.csvfile = open(filepath, 'wb')
        self.columns = columns
        self.fmtfunc = fmtfunc
        self.skipheader = skipheader
        self.writer = csv.writer(self.csvfile, **kwargs)

    def close(self):
        """Close writer"""
        self.csvfile.close()
        self.writer = None

    def __enter__(self):
        """Implementation of context manager API"""
        return self

    def __exit__(self, *args):
        """Implementation of context manager API"""
        self.close()

    def __rrshift__(self, iterable):
        """Write elements of iterable to file"""
        cols = self.columns
        iterable = iter(iterable)
        for _ in xrange(self.skipheader):
            next(iterable)
        for row in iterable:
            row = row if hasattr(row, '__iter__') else [row]
            row = [row[i] for i in cols] if cols else row
            self.writer.writerow(map(self.fmtfunc, row))
