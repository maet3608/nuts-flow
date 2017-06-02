"""
.. module:: test_function
   :synopsis: Unit tests for function module
"""

import pytest

from six.moves import range
from nutsflow import *
from nutsflow.common import Redirect


# Avoid importing numpy for the test of Print() only and use Fake instead.
class FakeNumpyArray(object):
    def __init__(self, data):
        self.data = data

    def ndim(self):
        return 1 if len(self.data) else 0

    def tolist(self):
        return self.data

    def item(self):
        return self.data


def np_array(data):
    return FakeNumpyArray(data)


def test_Identity():
    data = [0, 1, 2, 3]
    assert data >> Identity() >> Collect() == data


def test_Square():
    data = [0, 1, 2, 3]
    assert data >> Square() >> Collect() == [0, 1, 4, 9]


def test_NOP():
    data = [1, 2, 3]
    assert data >> NOP(Square) >> Collect() == data


def test_Get():
    data = [(1, 2, 3), (4, 5, 6)]
    assert data >> Get(None) >> Collect() == data
    assert data >> Get(0) >> Collect() == [1, 4]
    assert data >> Get(1) >> Collect() == [2, 5]
    assert data >> Get(0, 2) >> Collect() == [(1, 2), (4, 5)]
    assert data >> Get(0, 3, 2) >> Collect() == [(1, 3), (4, 6)]


def test_GetCols():
    data = [[1, 2, 3], [4, 5, 6]]
    assert data >> GetCols(1) >> Collect() == [(2,), (5,)]
    assert data >> GetCols(2, 0) >> Collect() == [(3, 1), (6, 4)]
    assert data >> GetCols(2, 1, 0) >> Collect() == [(3, 2, 1), (6, 5, 4)]
    assert data >> GetCols(1, 1) >> Collect() == [(2, 2), (5, 5)]


def test_Counter():
    counter = Counter('cnt')
    assert counter.value == 0

    range(10) >> counter >> Consume()
    assert counter.value == 10
    assert str(counter) == 'cnt = 10'

    counter.reset()
    assert counter.value == 0

    counter = Counter('cnt', filterfunc=lambda x: x < 3, value=1)
    range(10) >> counter >> Consume()
    assert counter.value == 4


def test_Sleep():
    start = time.time()
    assert range(10) >> Sleep(0.01) >> Collect() == list(range(10))
    duration = time.time() - start
    assert 0.05 < duration < 0.2


def test_Format():
    [] >> Format('{}') >> Collect() == []
    [1, 2, 3] >> Format('num:{}') >> Collect() == ['num:1', 'num:2', 'num:3']
    [(1, 2), (3, 4)] >> Format('{0}:{1}') >> Collect() == ['1:2', '3:4']


def test_Print():
    with Redirect() as _:
        assert [1, 2, 3] >> Print() >> Collect() == [1, 2, 3]

    with Redirect() as out:
        data = [np_array(1), np_array(2)]
        data >> Print() >> Consume()
    assert out.getvalue() == '1\n2\n'

    with Redirect() as out:
        data = [np_array([1, 2]), np_array([3, 4])]
        data >> Print('{1}:{0}') >> Consume()
    assert out.getvalue() == '2:1\n4:3\n'

    with Redirect() as out:
        [1, 2, 3] >> Print() >> Consume()
    assert out.getvalue() == '1\n2\n3\n'

    with Redirect() as out:
        range(10) >> Print(every_n=3) >> Consume()
    assert out.getvalue() == '2\n5\n8\n'

    with Redirect() as out:
        even = lambda x: x % 2 == 0
        [1, 2, 3, 4] >> Print(filterfunc=even) >> Consume()
    assert out.getvalue() == '2\n4\n'

    with Redirect() as out:
        [1, 2, 3, 4] >> Sleep(0.1) >> Print(every_sec=0.15) >> Consume()
    assert out.getvalue() == '2\n4\n'

    with Redirect() as out:
        [1, 2, 3] >> Print('num:{}') >> Consume()
    assert out.getvalue() == 'num:1\nnum:2\nnum:3\n'

    with Redirect() as out:
        fmt = lambda x: 'num:' + str(x)
        [1, 2, 3] >> Print(fmt) >> Consume()
    assert out.getvalue() == 'num:1\nnum:2\nnum:3\n'

    with Redirect() as out:
        [(1, 2), (3, 4)] >> Print('{1}:{0}') >> Consume()
    assert out.getvalue() == '2:1\n4:3\n'

    with pytest.raises(ValueError) as ex:
        [1, 2, 3] >> Print(['invalid']) >> Consume()
    assert str(ex.value) == "Invalid format ['invalid']"
