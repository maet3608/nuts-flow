"""
.. module:: sink
   :synopsis: Nuts that reads streams and potentially produce non-stream output.
"""
from __future__ import absolute_import

import csv
import math
import six

import collections as cl

from six.moves import reduce, zip, range
from .base import NutSink
from .factory import nut_sink
from .common import as_tuple, is_iterable, colfunc
from .iterfunction import nth, consume, length, take


@nut_sink
def Sort(iterable, key=None, reverse=False):
    """
    iterable >> Sort(key=None, reverse=False)

    Sorts iterable with respect to key function or column index(es).

    >>> [3, 1, 2] >> Sort()
    [1, 2, 3]

    >>> [3, 1, 2] >> Sort(reverse=True)
    [3, 2, 1]

    >>> [(1,'c'), (2,'b'), (3,'a')] >> Sort(1)
    [(3, 'a'), (2, 'b'), (1, 'c')]

    >>> ['a3', 'c1', 'b2'] >> Sort(key=lambda s: s[0])
    ['a3', 'b2', 'c1']

    >>> ['a3', 'c1', 'b2'] >> Sort(key=0)
    ['a3', 'b2', 'c1']

    >>> ['a3', 'c1', 'b2'] >> Sort(1)
    ['c1', 'b2', 'a3']

    >>> ['a3', 'c1', 'b2'] >> Sort((1,0))
    ['c1', 'b2', 'a3']

    :param iterable iterable: Iterable
    :param int|tuple|function|None key: function to sort based on or
           column index(es) tuples/vectors/strings are sorted by.
    :param boolean reverse: True: reverse order.
    :return: Sorted iterable
    :rtype: list
    """
    return sorted(iterable, key=colfunc(key), reverse=reverse)


@nut_sink
def Sum(iterable, key=None):
    """
    iterable >> Sum(key=None)

    Return sum over inputs (transformed or extracted by key function)

    >>> [1, 2, 3] >> Sum()
    6

    >>> [1, 2, 3] >> Sum(lambda x: x*x)
    14

    >>> data = [(1, 10), (2, 20), (3, 30)]
    >>> data >> Sum(key=0)
    6
    >>> data >> Sum(key=1)
    60

    :param iterable iterable: Iterable over numbers
    :param int|tuple|function|None key: Key function to extract elements.
    :return: Sum of numbers
    :rtype: number
    """
    return sum(map(colfunc(key), iterable))


@nut_sink
def Mean(iterable, key=None, default=None):
    """
    iterable >> Mean(key=None, default=None)

    Return mean value of inputs (transformed or extracted by key function).

    >>> [1, 2, 3] >> Mean()
    2.0

    >>> [] >> Mean(default=0)
    0

    >>> data = [(1, 10), (2, 20), (3, 30)]
    >>> data >> Mean(key=0)
    2.0
    >>> data >> Mean(key=1)
    20.0

    :param iterable iterable: Iterable over numbers
    :param object default: Value returned if iterable is empty.
    :param int|tuple|function|None key: Key function to extract elements.
    :return: Mean of numbers or default value
    :rtype: number
    """
    f = colfunc(key)
    sum, n = 0, 0
    for e in iterable:
        sum += f(e)
        n += 1
    return float(sum) / n if n else default


@nut_sink
def MeanStd(iterable, key=None, default=None, ddof=1):
    """
    iterable >> MeanStd(key=None, default=None, ddof=1)

    Return mean and standard deviation of inputs (transformed or extracted
    by key function).
    Standard deviation is with degrees of freedom = 1

    >>> [1, 2, 3] >> MeanStd()
    (2.0, 1.0)

    >>> data = [(1, 10), (2, 20), (3, 30)]
    >>> data >> MeanStd(key=0)
    (2.0, 1.0)
    >>> data >> MeanStd(1)
    (20.0, 10.0)

    :param iterable iterable: Iterable over numbers
    :param object default: Value returned if iterable is empty.
    :param int|tuple|function|None key: Key function to extract elements.
    :param int ddof: Delta degrees of freedom (should 0 or 1)
    :return: Mean and standard deviation of numbers or default value
    :rtype: tuple (mean, std)
    """
    f = colfunc(key)
    sume, sqre, n = 0.0, 0.0, 0.0
    for e in iterable:
        e = f(e)
        sume += e
        sqre += e * e
        n += 1.0
    if n - ddof <= 0:
        return default
    avg = sume / n
    dev = math.sqrt((n * sqre - sume * sume) / (n * (n - ddof)))
    return avg, dev


@nut_sink
def Max(iterable, key=None, default=None):
    """
    iterable >> Max(key=None, default=None)

    Return maximum of inputs (transformed or extracted by key function).

    >>> [1, 2, 3, 2] >> Max()
    3

    >>> ['1', '123', '12'] >> Max(key=len)
    '123'

    >>> [] >> Max(default=0)
    0

    >>> data = [(3, 10), (2, 20), (1, 30)]
    >>> data >> Max(key=0)
    (3, 10)

    >>> data >> Max(1)
    (1, 30)


    :param iterable iterable: Iterable over numbers
    :param int|tuple|function|None key: Key function to extract or
           transform elements. None = identity function.
    :param object default: Value returned if iterable is empty.
    :return: largest element according to key function
    :rtype: object
    """
    try:
        return max(iterable, key=colfunc(key))
    except Exception:
        return default


@nut_sink
def Min(iterable, key=None, default=None):
    """
    iterable >> Min(key=None, default=None)

    Return minimum of inputs (transformed or extracted by key function).

    >>> [1, 2, 3, 2] >> Min()
    1

    >>> ['1', '123', '12'] >> Min(key=len)
    '1'

    >>> [] >> Min(default=0)
    0

    >>> data = [(3, 10), (2, 20), (1, 30)]
    >>> data >> Min(key=0)
    (1, 30)

    >>> data >> Min(1)
    (3, 10)


    :param iterable iterable: Iterable over numbers
    :param int|tuple|function|None key: Key function to extract or
           transform elements. None = identity function.
    :param object default: Value returned if iterable is empty.
    :return: smallest element according to key function
    :rtype: object
    """
    try:
        return min(iterable, key=colfunc(key))
    except Exception:
        return default


@nut_sink
def ArgMax(iterable, key=None, default=None, retvalue=False):
    """
    iterable >> ArgMax(key=None, default=None, retvalue=False)

    Return index of first maximum element (and maximum) in input
    (transformed or extracted by key function).

    >>> [1, 2, 0, 2] >> ArgMax()
    1

    >>> ['12', '1', '123'] >> ArgMax(key=len, retvalue=True)
    (2, '123')

    >>> ['12', '1', '123'] >> ArgMax(key=len)
    2

    >>> [] >> ArgMax(default=0)
    0

    >>> [] >> ArgMax(default=(None, 0), retvalue=True)
    (None, 0)

    >>> data = [(3, 10), (2, 20), (1, 30)]
    >>> data >> ArgMax(key=0)
    0
    >>> data >> ArgMax(1)
    2

    :param iterable iterable: Iterable over numbers
    :param int|tuple|function|None key: Key function to extract or
           transform elements. None = identity function.
    :param object default: Value returned if iterable is empty.
    :param bool retvalue: If True the index and the value of the
           maximum element is returned.
    :return: index of largest element according to key function
             and the largest element itself if retvalue==True
    :rtype: object | tuple
    """
    try:
        f = colfunc(key)
        i, v = max(enumerate(iterable), key=lambda i_e: f(i_e[1]))
        return (i, v) if retvalue else i
    except Exception:
        return default


@nut_sink
def ArgMin(iterable, key=None, default=None, retvalue=False):
    """
    iterable >> ArgMin(key=None, default=None, retvalue=True)

    Return index of first minimum element (and minimum) in input
    (transformed or extracted by key function).

    >>> [1, 2, 0, 2] >> ArgMin()
    2

    >>> ['12', '1', '123'] >> ArgMin(key=len, retvalue=True)
    (1, '1')

    >>> ['12', '1', '123'] >> ArgMin(key=len)
    1

    >>> [] >> ArgMin(default=0)
    0

    >>> [] >> ArgMin(default=(None, 0), retvalue=True)
    (None, 0)

    >>> data = [(3, 10), (2, 20), (1, 30)]
    >>> data >> ArgMin(key=0)
    2
    >>> data >> ArgMin(1)
    0


    :param iterable iterable: Iterable over numbers
    :param int|tuple|function|None key: Key function to extract or
           transform elements. None = identity function.
    :param object default: Value returned if iterable is empty.
    :param bool retvalue: If True the index and the value of the
           minimum element is returned.
    :return: index of smallest element according to key function
             and the smallest element itself if retvalue==True.
    :rtype: object | tuple
    """
    try:
        f = colfunc(key)
        i, v = min(enumerate(iterable), key=lambda i_e1: f(i_e1[1]))
        return (i, v) if retvalue else i
    except Exception:
        return default


Reduce = nut_sink(reduce, 1)
"""
iterable >> Reduce(func [,initiaizer])

Reduces the iterable using the given function.
See https://docs.python.org/2/library/functions.html#reduce

>>> [1, 2, 3] >> Reduce(lambda a,b: a+b)
6

>>> [2] >> Reduce(lambda a,b: a*b, 1)
2

:param iterable iterable: Any iterable
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

:param iterable iterable: Any iterable
:param int nth: Index of element in iterable to return
:return: n-th element
:rtype: any
"""

Next = nut_sink(next)
"""
iterable >> Next()

Return next element of iterable.

>>> [1,2,3] >> Next()
1

:param iterable iterable: Any iterable
:return: next element
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

Count = nut_sink(length)
"""
iterable >> Count()

Return number elements in input iterable.  This consumes the iterable!

>>> [0, 1, 2] >> Count()
3

:param iterable iterable: Any iterable
:return: Number elements in interable
:rtype: int
"""


@nut_sink
def Unzip(iterable, container=None):
    """
    iterable >> Unzip(container=None)

    Same as izip(*iterable) but returns iterators for container=None

    >>> [(1, 2, 3), (4, 5, 6)] >> Unzip(tuple) >> Collect()
    [(1, 4), (2, 5), (3, 6)]

    :param iterable iterable:  Any iterable, e.g. list, range, ...
    :param container container: If not none, unzipped results are collected
       in the provided container, eg. list, tuple, set
    :return: Unzip iterable.
    :rtype: iterator over iterators
    """
    unzipped = zip(*iterable)
    return map(container, unzipped) if container else unzipped


@nut_sink
def Head(iterable, n, container=list):
    """
    iterable >> Head(n, container=list)

    Collect first n elements of iterable in specified container.

    >>> [1, 2, 3, 4] >> Head(2)
    [1, 2]

    :param iterable iterable: Any iterable, e.g. list, range, ...
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
    [3, 4]

    :param iterable iterable: Any iterable, e.g. list, range, ...
    :param int n: Number of elements to take.
    :param container container: Container to collect elements in, e.g. list, set
    :return: Container with tail elements
    :rtype: container
    """
    return container(cl.deque(iterable, n))


@nut_sink
def CountValues(iterable, column=None, relative=False):
    """
    iterable >> CountValues(relative=False)

    Return dictionary with (relative) counts of the values
    in the input iterable.

    >>> 'abaacc' >> CountValues()  # doctest: +SKIP
    {'a': 3, 'b': 1, 'c': 2}

    >>> 'aabaab' >> CountValues(relative=True)  # doctest: +SKIP
    {'a': 1.0, 'b': 0.5}

    >>> data = [('a', 'X'), ('b', 'Y'), ('a', 'Y')]
    >>> data >> CountValues(column=0)  # doctest: +SKIP
    {'a': 2, 'b': 1}
    >>> data >> CountValues(column=1)  # doctest: +SKIP
    {'Y': 2, 'X': 1}

    :param iterable iterable: Any iterable, e.g. list, range, ...
    :param int|None column: Column of values in iterable to extract values from.
       If colum=None the values in the iterable themselves will be counted.
    :param bool relative: True: return relative counts otherwise absolute counts
    :return: Dictionary with (relative) counts for elements in iterable.
    :rtype: dict
    """
    values = iterable if column is None else (i[column] for i in iterable)
    cnts = dict(cl.Counter(values))
    if not relative or not cnts.values():
        return cnts
    max_cnt = max(cnts.values())
    n = float(max_cnt) if max_cnt else 1.0
    return {k: v / n for k, v in six.iteritems(cnts)}


@nut_sink
def Collect(iterable, container=list):
    """
    iterable >> Collect(container)

    Collects all elements of the iterable input in the given container.

    >>> range(5) >> Collect()
    [0, 1, 2, 3, 4]

    >>> [1, 2, 3, 2] >> Collect(set)  # doctest: +SKIP
    {1, 2, 3}

    >>> [('one', 1), ('two', 2)] >> Collect(dict)  # doctest: +SKIP
    {'one': 1, 'two': 2}

    :param iterable iterable: Any iterable, e.g. list, range, ...
    :param container container: Some container, e.g. list, set, dict
           that can be filled from an iterable
    :return: Container
    :rtype: container
    """
    return container(iterable)


@nut_sink
def Join(iterable, separator=''):
    """
    iterable >> Join(separator='')

    Same as Python's sep.join(iterable). Concatenates the elements in
    the iterable to a string using the given separator. In addition to
    Python's sep.join(iterable) it also automatically converts elements
    to strings.

    :param iterable iterable: Any iterable
    :param string separator: Seperator string between elements.
    :return: String of with concatenated elements of iterable.
    :rtype: str
    """
    return separator.join(map(str, iterable))


class WriteCSV(NutSink):
    """
    Write data to a CSV file using Python's CSV writer.
    See: https://docs.python.org/2/library/csv.html
    """

    def __init__(self, filepath, cols=None, skipheader=0, flush=False,
                 fmtfunc=lambda x: x, **kwargs):
        """
        WriteCSV(filepath, cols, skipheader, flush, fmtfunc, **kwargs)

        Write data in Comma Separated Values format (CSV) and other formats
        to file. Tab Separated Values (TSV) files can be written by
        specifying a different delimiter. Note that in the docstring below
        delimiter is '\\t' but in code it should be '\t'. See unit tests.

        Also see https://docs.python.org/2/library/csv.html
        and ReadCSV.


        >>> import os
        >>> filepath = 'tests/data/temp_out.csv'
        >>> with WriteCSV(filepath) as writer:
        ...     range(10) >> writer
        >>> os.remove(filepath)

        >>> with WriteCSV(filepath, cols=(1,0)) as writer:
        ...     [(1,2), (3,4)] >> writer
        >>> os.remove(filepath)

        >>> filepath = 'tests/data/temp_out.tsv'
        >>> with WriteCSV(filepath, delimiter='\\t') as writer:
        ...     [[1,2], [3,4]] >> writer
        >>> os.remove(filepath)


        :param string filepath: Path to file in CSV format.
        :param tuple cols: Indices of the columns to write.
                           If None all columns are written.
        :param int skipheader: Number of header rows to skip.
        :param bool flush: If True flush after every line written.
        :param function fmtfunc: Function to apply to the elements of each row.
        :param kwargs kwargs: Keyword arguments for Python's CSV writer.
                              See https://docs.python.org/2/library/csv.html
        """
        self.csvfile = open(filepath, 'w')
        self.columns = cols if cols is None else as_tuple(cols)
        self.flush = flush
        self.fmtfunc = fmtfunc
        self.skipheader = skipheader
        self.writer = csv.writer(self.csvfile, lineterminator='\n', **kwargs)

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
        for _ in range(self.skipheader):
            next(iterable)
        for row in iterable:
            row = row if is_iterable(row) else [row]
            row = [row[i] for i in cols] if cols else row
            self.writer.writerow([self.fmtfunc(r) for r in row])
            if self.flush:
                self.csvfile.flush()
