"""
.. module:: test_source
   :synopsis: Unit tests for source module
"""

from nutsflow import *


def test_Steps():
    assert Steps() >> Take(3) >> Collect() == [0, 1, 2]
    assert Steps(1, 2) >> Take(3) >> Collect() == [1, 3, 5]


def test_Repeat():
    assert Repeat(1) >> Take(4) >> Collect() == [1, 1, 1, 1]
    assert Repeat(1, 3) >> Collect() == [1, 1, 1]


def test_Product():
    result = [('a', 0), ('a', 1), ('a', 2), ('b', 0), ('b', 1), ('b', 2)]
    assert Product('ab', xrange(3)) >> Collect() == result


def test_Empty():
    assert Empty() >> Collect() == []


def test_Range():
    assert Range(4) >> Collect() == [0, 1, 2, 3]
    assert Range(1, 5) >> Collect() == [1, 2, 3, 4]


def test_CSVReader():
    filepath = 'tests/data/data.csv'
    with CSVReader(filepath) as reader:
        assert reader >> Collect() == [('a', ' ', 'c'),
                                       ('1', '2', '3'),
                                       ('4', '5', '6')]
    with CSVReader(filepath, skipheader=1, fmtfunc=int) as reader:
        assert reader >> Collect() == [(1, 2, 3), (4, 5, 6)]
    with CSVReader(filepath, columns=(2, 1)) as reader:
        assert reader >> Collect() == [('c', ' '), ('3', '2'), ('6', '5')]


def test_CSVReader_tsv():
    filepath = 'tests/data/data.tsv'
    with CSVReader(filepath, delimiter='\t') as reader:
        assert reader >> Collect() == [('a', ' ', 'c'),
                                       ('1', '2', '3'),
                                       ('4', '5', '6')]
    with CSVReader(filepath, skipheader=1, fmtfunc=int,
                   delimiter='\t') as reader:
        assert reader >> Collect() == [(1, 2, 3), (4, 5, 6)]
