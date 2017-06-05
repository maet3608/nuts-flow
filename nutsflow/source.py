"""
.. module:: source
   :synopsis: Nuts that produce iterables but do not take input iterables.
"""
from __future__ import absolute_import

import csv

import itertools as itt
import nutsflow.iterfunction as itf

from six.moves import range
from .base import NutSource
from .factory import nut_source
from .common import as_tuple


@nut_source
def Enumerate(start=0, step=1):
    """
    Enumerate(start=0 [, step])

    Return increasing integers. See itertools.count
    
    >>> from nutsflow import Take, Collect

    >>> Enumerate() >> Take(3) >> Collect()
    [0, 1, 2]

    >>> Enumerate(1, 2) >> Take(3) >> Collect()
    [1, 3, 5]

    :param int start: Start of integer sequence
    :param int step: Step of sequence
    :return: Increasing integers.
    :rtype: iterable over int
    """
    return itt.count(start, step=step)


@nut_source
def Repeat(value, n=None):
    """
    Repeat(value [, n])

    Return given value repeatedly. See itertools.repeat
    
    >>> from nutsflow import Take, Collect

    >>> Repeat(1, 3) >> Collect()
    [1, 1, 1]

    >>> Repeat(1) >> Take(4) >> Collect()
    [1, 1, 1, 1]

    :param object value: Value to repeat
    :param int times: Optional parameter. Object is repeated 'n' times.
    :return: Iterator of repeated objects
    :rtype: iterable over object
    """
    return itt.repeat(value, n) if n else itt.repeat(value)


@nut_source
def Product(*args, **kwds):
    """
    Product(*iterables [, repeat])

    Return cartesian product of input iterables.

    >>> from nutsflow import Collect
    
    >>> Product([1, 2], [3, 4]) >> Collect()
    [(1, 3), (1, 4), (2, 3), (2, 4)]

    >>> Product('ab', range(3)) >> Collect()
    [('a', 0), ('a', 1), ('a', 2), ('b', 0), ('b', 1), ('b', 2)]

    >>> Product([1, 2, 3], repeat=2) >> Collect()
    [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3)]

    :param iterables iterables: Collections of iterables to create cartesian
            product from.
    :param int repeat: Repeat a single iterable 'repeat' times, e.g.
            Procuct([1,2], [1,2]) is equal to Product([1,2], repeat=2)
    :return: cartesian product
    :rtype: iterator over tuples
    """
    return itt.product(*args, **kwds)


@nut_source
def Empty():
    """
    Empty()

    Return empty iterable.

    >>> from nutsflow import Collect
    >>> Empty() >> Collect()
    []

    :return: Empty iterator
    :rtype: iterator
    """
    return iter(())


class Range(NutSource):
    """
    Range of numbers. Similar to range() but returns iterator that depletes.
    """

    def __init__(self, *args, **kwargs):
        """
        Range(start [,end [, step]])

        Return range of integers.

        >>> from nutsflow import Collect
        >>> Range(4) >> Collect()
        [0, 1, 2, 3]

        >>> Range(1, 5) >> Collect()
        [1, 2, 3, 4]

        :param int start: Start of range.
        :param int end: End of range. Not inclusive. Optional.
        :param int step: Step size. Optional.
        :return: Range of integers.
        :rtype: iterable over int
        """
        self.iter = iter(range(*args, **kwargs))

    def __iter__(self):
        """Return iterator over numbers."""
        return self.iter


class ReadCSV(NutSource):
    """
    Read data from a CSV file using Python's CSV reader.
    See: https://docs.python.org/2/library/csv.html
    """

    def __init__(self, filepath, columns=None, skipheader=0,
                 fmtfunc=lambda x: x, **kwargs):
        """
        ReadCSV(filepath, columns, skipheader, fmtfunc, **kwargs)

        Read data in Comma Separated Format (CSV) from file.
        See also CSVWriter.
        Can also read Tab Separated Format (TSV) be providing the
        corresponding delimiter. Note that in the docstring below
        delimiter is '\\t' but in code it should be '\t'. See unit tests.

        >>> from nutsflow import Collect
        >>> filepath = 'tests/data/data.csv'
        >>> with ReadCSV(filepath, skipheader=1, fmtfunc=int) as reader:
        ...     reader >> Collect()
        [(1, 2, 3), (4, 5, 6)]

        >>> with ReadCSV(filepath, (2, 1), 1, int) as reader:
        ...     reader >> Collect()
        [(3, 2), (6, 5)]

        >>> with ReadCSV(filepath, 2, 1, int) as reader:
        ...     reader >> Collect()
        [3, 6]

        >>> filepath = 'tests/data/data.tsv'
        >>> with ReadCSV(filepath, skipheader=1, fmtfunc=int,
        ...                delimiter='\\t') as reader:
        ...     reader >> Collect()
        [(1, 2, 3), (4, 5, 6)]

        :param string filepath: Path to file in CSV format.
        :param tuple columns: Indices of the columns to read.
                              If None all columns are read.
        :param int skipheader: Number of header lines to skip.
        :param function fmtfunc: Function to apply to the elements of each row.
        :param kwargs kwargs: Keyword arguments for Python's CSV reader.
                              See https://docs.python.org/2/library/csv.html
        """
        self.csvfile = open(filepath, 'r')
        self.columns = columns if columns is None else as_tuple(columns)
        self.fmtfunc = fmtfunc
        for _ in range(skipheader):
            next(self.csvfile)
        itf.take(self.csvfile, skipheader)
        stripped = (r.strip() for r in self.csvfile)
        self.reader = csv.reader(stripped, **kwargs)

    def close(self):
        """Close reader"""
        self.csvfile.close()
        self.reader = None

    def __enter__(self):
        """Implementation of context manager API"""
        return self

    def __exit__(self, *args):
        """Implementation of context manager API"""
        self.close()

    def __iter__(self):
        """Return iterator over rows in CSV file."""
        cols = self.columns
        for row in self.reader:
            row = [row[i] for i in cols] if cols else row
            row = [self.fmtfunc(r) for r in row]
            yield tuple(row) if len(row) > 1 else row[0]
