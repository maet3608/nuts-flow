"""
.. module:: test_sink
   :synopsis: Unit tests for sink module
"""

import os
import pytest

from six.moves import range
from nutsflow import *


def assert_equal_text(text1, text2):
    assert text1.splitlines() == text2.splitlines()


def test_Sort():
    assert [] >> Sort() == []
    assert [3, 1, 2] >> Sort() == [1, 2, 3]
    assert [3, 1, 2] >> Sort(reverse=True) == [3, 2, 1]
    assert ['a3', 'c1', 'b2'] >> Sort(key=0) == ['a3', 'b2', 'c1']
    assert ['a3', 'c1', 'b2'] >> Sort(key=1) == ['c1', 'b2', 'a3']


def test_Sum():
    assert [] >> Sum() == 0

    data = [1, 2, 3]
    assert data >> Sum() == 6
    assert data >> Sum(key=lambda x: x * x) == 14

    data = [(1, 10), (2, 20), (3, 30)]
    assert data >> Sum(key=0) == 6
    assert data >> Sum(key=1) == 60
    assert data >> Sum(key=lambda x: x[0] + x[1]) == 66


def test_Mean():
    assert [] >> Mean() is None
    assert [] >> Mean(default=0) == 0
    assert [1, 2, 3] >> Mean() == pytest.approx(2.0, rel=1e-2)

    data = [(1, 10), (2, 20), (3, 30)]
    assert data >> Mean(key=0) == pytest.approx(2.0, rel=1e-2)
    assert data >> Mean(key=1) == pytest.approx(20.0, rel=1e-2)


def test_MeanStd():
    assert [] >> MeanStd() is None
    assert [] >> MeanStd(ddof=1) is None
    assert [] >> MeanStd(default=0) == 0

    assert [1, 2, 3] >> MeanStd() == pytest.approx([2.0, 1.0], rel=1e-2)
    assert [1, 2, 3] >> MeanStd(ddof=0) == pytest.approx([2.0, 0.81], rel=1e-2)

    data = [(1, 10), (2, 20), (3, 30)]
    assert data >> MeanStd(key=0) == pytest.approx([2.0, 1.0], rel=1e-2)
    assert data >> MeanStd(key=1) == pytest.approx([20.0, 10.0], rel=1e-2)


def test_Max():
    assert [] >> Max(default=0) == 0
    assert [0, 3, 2] >> Max() == 3
    assert ['1', '123', '12'] >> Max(key=len) == '123'

    data = [(3, 10), (2, 20), (1, 30)]
    assert data >> Max(key=0) == (3, 10)
    assert data >> Max(key=1) == (1, 30)


def test_Min():
    assert [] >> Min(default=0) == 0
    assert [3, 1, 2] >> Min() == 1
    assert ['123', '1', '12'] >> Min(key=len) == '1'

    data = [(3, 10), (2, 20), (1, 30)]
    assert data >> Min(key=0) == (1, 30)
    assert data >> Min(key=1) == (3, 10)


def test_ArgMax():
    assert [] >> ArgMax(default=0) == 0
    assert [] >> ArgMax(default=(None, 0)) == (None, 0)

    assert [0, 3, 2] >> ArgMax() == 1

    assert ['1', '123', '12'] >> ArgMax(key=len) == 1
    assert ['1', '123', '12'] >> ArgMax(key=len, retvalue=True) == (1, '123')

    data = [(3, 10), (2, 20), (1, 30)]
    assert data >> ArgMax(key=0) == 0
    assert data >> ArgMax(key=1) == 2


def test_ArgMin():
    assert [] >> ArgMin(default=0) == 0
    assert [] >> ArgMin(default=(None, 0)) == (None, 0)

    assert [3, 1, 2] >> ArgMin() == 1

    assert ['123', '1', '12'] >> ArgMin(key=len) == 1
    assert ['123', '1', '12'] >> ArgMin(key=len, retvalue=True) == (1, '1')

    data = [(3, 10), (2, 20), (1, 30)]
    assert data >> ArgMin(key=0) == 2
    assert data >> ArgMin(key=1) == 0


def test_Reduce():
    assert [] >> Reduce(lambda a, b: a + b, None) == None
    assert [0, 1, 2] >> Reduce(lambda a, b: a + b) == 3
    assert [2] >> Reduce(lambda a, b: a * b, 1) == 2


def test_Nth():
    assert [0, 1, 2, 3] >> Nth(2) == 2


def test_Next():
    it = iter([1, 2, 3])
    assert it >> Next() == 1
    assert it >> Next() == 2
    assert it >> Next() == 3


def test_Consume():
    it = iter([0, 1, 2])
    it >> Consume()
    assert next(it, None) is None


def test_Count():
    assert [] >> Count() == 0
    assert [0, 1, 2, 3] >> Count() == 4


def test_Unzip():
    expected = [(1, 4), (2, 5), (3, 6)]
    input = [(1, 2, 3), (4, 5, 6)]

    assert [] >> Unzip() >> Map(tuple) >> Collect() == []
    assert iter(input) >> Unzip() >> Map(tuple) >> Collect() == expected

    assert [] >> Unzip(tuple) >> Collect() == []
    assert iter(input) >> Unzip(tuple) >> Collect() == expected


def test_CountValues():
    assert [] >> CountValues() == dict()
    assert 'abaacc' >> CountValues() == {'a': 3, 'b': 1, 'c': 2}

    assert [] >> CountValues(relative=True) == dict()
    assert [2] >> CountValues(relative=True) == {2: 1.0}
    assert 'aabaab' >> CountValues(relative=True) == {'a': 1.0, 'b': 0.5}

    data = [('a', 'X'), ('b', 'Y'), ('a', 'Y')]
    assert data >> CountValues(column=0) == {'a': 2, 'b': 1}
    assert data >> CountValues(column=1) == {'Y': 2, 'X': 1}


def test_Collect():
    assert [] >> Collect() == []
    assert range(5) >> Collect() == [0, 1, 2, 3, 4]
    assert [1, 2, 3, 2] >> Collect(set) == {1, 2, 3}
    assert [('one', 1), ('two', 2)] >> Collect(dict) == {'one': 1, 'two': 2}


def test_Join():
    assert [] >> Join() == ''
    assert range(5) >> Join() == '01234'
    assert range(5) >> Join(',') == '0,1,2,3,4'


def test_WriteCSV():
    filepath = 'tests/data/data_out.csv'
    data = [[1, 2], [3, 4]]

    with WriteCSV(filepath) as writer:
        data >> writer
    assert_equal_text(open(filepath).read(), '1,2\n3,4\n')

    with WriteCSV(filepath, cols=(1, 0)) as writer:
        data >> writer
    assert_equal_text(open(filepath).read(), '2,1\n4,3\n')

    with WriteCSV(filepath, cols=1) as writer:
        data >> writer
    assert_equal_text(open(filepath).read(), '2\n4\n')

    with WriteCSV(filepath, fmtfunc=lambda x: x + 1) as writer:
        data >> writer
    assert_equal_text(open(filepath).read(), '2,3\n4,5\n')

    with WriteCSV(filepath, skipheader=1) as writer:
        data >> writer
    assert_equal_text(open(filepath).read(), '3,4\n')

    with WriteCSV(filepath) as writer:
        [1, 2, 3] >> writer
    assert_equal_text(open(filepath).read(), '1\n2\n3\n')

    os.remove(filepath)


def test_WriteCSV_flush():
    filepath = 'tests/data/data_out.tsv'
    data = [[1, 2], [3, 4]]

    with WriteCSV(filepath, delimiter='\t', flush=True) as writer:
        data >> writer
        assert_equal_text(open(filepath).read(), '1\t2\n3\t4\n')

    os.remove(filepath)


def test_WriteCSV_tsv():
    filepath = 'tests/data/data_out.tsv'
    data = [[1, 2], [3, 4]]

    with WriteCSV(filepath, delimiter='\t') as writer:
        data >> writer
    assert_equal_text(open(filepath).read(), '1\t2\n3\t4\n')

    os.remove(filepath)
