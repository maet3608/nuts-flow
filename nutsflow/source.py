"""
.. module:: source
   :synopsis: Nuts that produce iterables but do not take input iterables.
"""

import csv

import itertools as itt
import iterfunction as itf

from base import NutSource
from factory import nut_source

Enumerate = nut_source(itt.count)
"""
Enumerate(start, step)

Return increasing integers. See itertools.count

>>> Enumerate() >> Take(3) >> Collect()
[0, 1, 2]

>>> Enumerate(1, 2) >> Take(3) >> Collect()
[1, 3, 5]

:param int start: Start of integer sequence
:param int step: Step of sequence
:return: Increasing integers.
:rtype: iterable over int
"""

Repeat = nut_source(itt.repeat)
"""
Repeat(object)

Return given object repeatly. See itertools.repeat

>>> Repeat(1, 3) >> Collect()
[1, 1, 1]

>>> Repeat(1) >> Take(4) >> Collect()
[1, 1, 1, 1]

:param object object: Object to repeat
:param int times: Optional parameter. Object is repeated 'times' times.
:return: Iterator of repeated objects
:rtype: iterable over object
"""

Product = nut_source(itt.product)
"""
Product(*iterables)

Return cartesian product of iterables. See itertools.product

>>> Product('ab', xrange(3)) >> Collect()
[('a', 0), ('a', 1), ('a', 2), ('b', 0), ('b', 1), ('b', 2)]

:param iterables iterables: Iterables
:return: Iterator over cartesian product
:rtype: iterable over object
"""


@nut_source
def Empty():
    """
    Empty()

    Return empty iterable.

    >>> Empty() >> Collect()
    []

    :return: Empty iterator
    :rtype: iterator
    """
    return iter(())


@nut_source
def Range(*args, **kwargs):
    """
    Range(start [,end [, step]])

    Return range of integers. Same a xrange()

    >>> Range(4) >> Collect()
    [0, 1, 2, 3]

    >>> Range(1,5) >> Collect()
    [1, 2, 3, 4]

    :param int start: Start of range.
    :param int end: End of range. Not inclusive. Optional.
    :param int step: Step size. Optional.
    :return: Range of integers.
    :rtype: iterable over int
    """
    return iter(xrange(*args, **kwargs))


class CSVReader(NutSource):
    """
    Read data from a CSV file using Python's CSV reader.
    See: https://docs.python.org/2/library/csv.html
    """

    def __init__(self, filepath, columns=None, skipheader=0,
                 fmtfunc=lambda x: x, **kwargs):
        """
        CSVReader(filepath, columns, skipheader, fmtfunc, **kwargs)

        Read data in Comma Separated Format (CSV) from file.
        See also CSVWriter.
        Can also read Tab Separated Format (TSV) be providing the
        corresponding delimiter. Note that in the docstring below
        delimiter is '\\t' but in code it should be '\t'. See unit tests.

        >>> from nutsflow import Collect
        >>> filepath = 'tests/data/data.csv'
        >>> with CSVReader(filepath, skipheader=1, fmtfunc=int) as reader:
        ...     reader >> Collect()
        [(1, 2, 3), (4, 5, 6)]

        >>> with CSVReader(filepath, (2, 1), 1, int) as reader:
        ...     reader >> Collect()
        [(3, 2), (6, 5)]

        >>> filepath = 'tests/data/data.tsv'
        >>> with CSVReader(filepath, skipheader=1, fmtfunc=int,
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
        self.csvfile = open(filepath, 'rb')
        self.columns = columns
        self.fmtfunc = fmtfunc
        for _ in xrange(skipheader): next(self.csvfile)
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
            yield tuple(map(self.fmtfunc, row))
