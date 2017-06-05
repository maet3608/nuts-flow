"""
.. module:: test_source
   :synopsis: Unit tests for source module
"""

from six.moves import range
from nutsflow import *


def test_Enumerate():
    assert Enumerate() >> Take(3) >> Collect() == [0, 1, 2]
    assert Enumerate(1, 2) >> Take(3) >> Collect() == [1, 3, 5]


def test_Repeat():
    assert Repeat(1) >> Take(4) >> Collect() == [1, 1, 1, 1]
    assert Repeat(1, 3) >> Collect() == [1, 1, 1]


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
        assert reader >> Collect() == [('a', ' ', 'c'),
                                       ('1', '2', '3'),
                                       ('4', '5', '6')]
    with ReadCSV(filepath, skipheader=1, fmtfunc=int) as reader:
        assert reader >> Collect() == [(1, 2, 3), (4, 5, 6)]
    with ReadCSV(filepath, columns=(2, 1)) as reader:
        assert reader >> Collect() == [('c', ' '), ('3', '2'), ('6', '5')]
    with ReadCSV(filepath, columns=0) as reader:
        assert reader >> Collect() == ['a', '1', '4']


def test_ReadCSV_tsv():
    filepath = 'tests/data/data.tsv'
    with ReadCSV(filepath, delimiter='\t') as reader:
        assert reader >> Collect() == [('a', ' ', 'c'),
                                       ('1', '2', '3'),
                                       ('4', '5', '6')]
    with ReadCSV(filepath, skipheader=1, fmtfunc=int,
                 delimiter='\t') as reader:
        assert reader >> Collect() == [(1, 2, 3), (4, 5, 6)]
