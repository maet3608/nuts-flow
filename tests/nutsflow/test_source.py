"""
.. module:: test_source
   :synopsis: Unit tests for source module
"""

from six.moves import range
from collections import namedtuple
from nutsflow import *


def test_Enumerate():
    assert Enumerate() >> Take(3) >> Collect() == [0, 1, 2]
    assert Enumerate(1, 2) >> Take(3) >> Collect() == [1, 3, 5]


def test_Repeat():
    assert Repeat(1) >> Take(4) >> Collect() == [1, 1, 1, 1]

    fx = lambda x: x
    assert Repeat(fx, 2) >> Take(3) >> Collect() == [2, 2, 2]


def test_Product():
    assert Product([]) >> Collect() == []

    result = [('a', 0), ('a', 1), ('a', 2), ('b', 0), ('b', 1), ('b', 2)]
    assert Product('ab', range(3)) >> Collect() == result

    result = [(1, 1), (1, 2), (2, 1), (2, 2)]
    assert Product([1, 2], repeat=2) >> Collect() == result


def test_Empty():
    assert Empty() >> Collect() == []


def test_Range():
    numbers = Range(3)
    assert numbers >> Take(2) >> Collect() == [0, 1]
    assert numbers >> Take(2) >> Collect() == [2]
    assert numbers >> Take(2) >> Collect() == []

    assert Range(4) >> Collect() == [0, 1, 2, 3]
    assert Range(1, 5) >> Collect() == [1, 2, 3, 4]


def test_ReadCSV():
    filepath = 'tests/data/data.csv'
    with ReadCSV(filepath) as reader:
        assert reader >> Collect() == [('A', 'B', 'C'),
                                       ('1', '2', '3'),
                                       ('4', '5', '6')]
    with ReadCSV(filepath, skipheader=1, fmtfunc=int) as reader:
        assert reader >> Collect() == [(1, 2, 3), (4, 5, 6)]
    with ReadCSV(filepath, skipheader=1, fmtfunc=(int, str, float)) as reader:
        assert reader >> Collect() == [(1, '2', 3.), (4, '5', 6.)]
    with ReadCSV(filepath, columns=(2, 1)) as reader:
        assert reader >> Collect() == [('C', 'B'), ('3', '2'), ('6', '5')]
    with ReadCSV(filepath, columns=0) as reader:
        assert reader >> Collect() == ['A', '1', '4']
    with ReadCSV(filepath, columns=0, skipheader=1, fmtfunc=(int,)) as reader:
        assert reader >> Collect() == [1, 4]


def test_ReadCSV_tsv():
    filepath = 'tests/data/data.tsv'
    with ReadCSV(filepath, delimiter='\t') as reader:
        assert reader >> Collect() == [('A', 'B', 'C'),
                                       ('1', '2', '3'),
                                       ('4', '5', '6')]
    with ReadCSV(filepath, skipheader=1, fmtfunc=int,
                 delimiter='\t') as reader:
        assert reader >> Collect() == [(1, 2, 3), (4, 5, 6)]


def test_ReadNamedCSV():
    filepath = 'tests/data/data.csv'
    Sample = namedtuple('Sample', 'A,B,C')
    with ReadNamedCSV(filepath, rowname='Sample') as reader:
        assert reader >> Collect() == [Sample(A='1', B='2', C='3'),
                                       Sample(A='4', B='5', C='6')]
    Row = namedtuple('Row', 'A,B,C')
    with ReadNamedCSV(filepath, fmtfunc=(int, float, str)) as reader:
        assert reader >> Collect() == [Row(A=1, B=2.0, C='3'),
                                       Row(A=4, B=5.0, C='6')]

    colnames = ('C', 'A')
    Row = namedtuple('Row', colnames)
    with ReadNamedCSV(filepath, colnames=colnames, fmtfunc=int) as reader:
        assert reader >> Collect() == [Row(C=3, A=1),
                                       Row(C=6, A=4)]

    Number = namedtuple('Row', 'A')
    with ReadNamedCSV(filepath, colnames=('A',), fmtfunc=(float,)) as reader:
        assert reader >> Collect() == [Number(A=1.0),
                                       Number(A=4.0)]
