"""
.. module:: test_processor
   :synopsis: Unit tests for processor module
"""
from __future__ import print_function

import pytest

import random as rnd

from six.moves import range
from nutsflow import *
from nutsflow import _
from nutsflow.common import Redirect


def test_Take():
    assert [] >> Take(0) >> Collect() == []
    assert [] >> Take(2) >> Collect() == []
    assert [1, 2, 3, 4] >> Take(0) >> Collect() == []
    assert [1, 2, 3, 4] >> Take(2) >> Collect() == [1, 2]


def test_Slice():
    assert [1, 2, 3, 4] >> Slice(0) >> Collect() == []
    assert [1, 2, 3, 4] >> Slice(2) >> Collect() == [1, 2]
    assert [1, 2, 3, 4] >> Slice(1, 3) >> Collect() == [2, 3]
    assert [1, 2, 3, 4] >> Slice(0, 4, 2) >> Collect() == [1, 3]


def test_Concat():
    assert [] >> Concat([]) >> Collect() == []
    assert [1, 2] >> Concat([]) >> Collect() == [1, 2]
    expected = ['1', '2', 'a', 'b', 'c', 'd', '+', '-']
    assert '12' >> Concat('abcd', '+-') >> Collect() == expected


def test_Interleave():
    assert [] >> Interleave([]) >> Collect() == []
    assert [1, 2] >> Interleave([]) >> Collect() == [1, 2]
    expected = ['1', 'a', '+', '2', 'b', '-', 'c', 'd']
    assert '12' >> Interleave('abcd', '+-') >> Collect() == expected


def test_Zip():
    assert [] >> Zip([]) >> Collect() == []

    expected = [(0, 'a'), (1, 'b'), (2, 'c')]
    assert [0, 1, 2] >> Zip('abc') >> Collect() == expected

    expected = [('1', 'a', '+'), ('2', 'b', '-')]
    assert '12' >> Zip('abcd', '+-') >> Collect() == expected


def test_ZipWith():
    add2 = lambda a, b: a + b
    add3 = lambda a, b, c: a + b + c

    assert [] >> ZipWith(add2, []) >> Collect() == []
    assert [1, 2, 3] >> ZipWith(add2, [2, 3, 4]) >> Collect() == [3, 5, 7]
    assert [1, 2] >> ZipWith(add3, [2, 3], [4, 5]) >> Collect() == [7, 10]


def test_Dedupe():
    assert [] >> Dedupe() >> Collect() == []
    assert [2, 3, 1, 1, 2, 4] >> Dedupe() >> Collect() == [2, 3, 1, 4]

    data = [(1, 'a'), (2, 'a'), (3, 'b')]
    expected = [(1, 'a'), (3, 'b')]
    assert data >> Dedupe(key=lambda t: t[1]) >> Collect() == expected
    assert data >> Dedupe(_[1]) >> Collect() == expected


def test_Cycle():
    assert [] >> Cycle() >> Take(5) >> Collect() == []
    assert [1, 2] >> Cycle() >> Take(5) >> Collect() == [1, 2, 1, 2, 1]


def test_Chunk():
    assert [] >> Chunk(2) >> Collect() == []
    expected = [(0, 1), (2, 3), (4, 5), (6,)]
    assert Range(7) >> Chunk(2) >> Map(tuple) >> Collect() == expected


def test_ChunkWhen():
    func = lambda x: x == '|'
    assert [] >> ChunkWhen(func) >> Map(list) >> Collect() == []
    expected = ['|12', '|345', '|6']
    '|12|345|6' >> ChunkWhen(func) >> Map(''.join) >> Collect() == expected
    expected = ['123456']
    assert '123456' >> ChunkWhen(func) >> Map(''.join) >> Collect() == expected


def test_ChunkBy():
    func = lambda x: x
    assert [] >> ChunkBy(func) >> Map(list) >> Collect() == []
    expected = [[1, 1], [2], [3, 3, 3]]
    [1, 1, 2, 3, 3, 3] >> ChunkBy(func) >> Map(list) >> Collect() == expected
    func = lambda x: x < 3
    expected = [[1, 1, 2], [3, 3, 3]]
    [1, 1, 2, 3, 3, 3] >> ChunkBy(func) >> Map(list) >> Collect() == expected
    expected = [[1, 2], [3], [1, 2], [3]]
    [1, 2, 3, 1, 2, 3] >> ChunkBy(func) >> Map(list) >> Collect() == expected


def test_Flatten():
    assert [] >> Flatten() >> Collect() == []
    assert [[], []] >> Flatten() >> Collect() == []
    assert [1, 2, 3] >> Flatten() >> Collect() == [1, 2, 3]
    assert [(1,), (2, 3), 4] >> Flatten() >> Collect() == [1, 2, 3, 4]
    assert [(1,), ((2, 3), 4)] >> Flatten() >> Collect() == [1, (2, 3), 4]


def test_FlattenCol():
    data = [([1, 2], [3, 4])]
    assert [] >> FlattenCol(0) >> Collect() == []
    assert data >> FlattenCol(0) >> Collect() == [(1,), (2,)]
    assert data >> FlattenCol((0, 1)) >> Collect() == [(1, 3), (2, 4)]
    assert data >> FlattenCol((1, 0)) >> Collect() == [(3, 1), (4, 2)]
    assert data >> FlattenCol((1, 1, 0)) >> Collect() == [(3, 3, 1), (4, 4, 2)]

    data = [([1, 2], 3)]
    assert data >> FlattenCol((0, 1)) >> Collect() == [(1, 3), (2, 3)]
    assert data >> FlattenCol(0) >> Collect() == [(1,), (2,)]


def test_FlatMap():
    assert [] >> FlatMap(_) >> Collect() == []
    assert [[1], [2]] >> FlatMap(_) >> Collect() == [1, 2]
    assert [[0], [1], [2]] >> FlatMap(_ * 2) >> Collect() == [0, 0, 1, 1, 2, 2]


def test_Map():
    assert [] >> Map(_) >> Collect() == []
    assert [0, 1, 2] >> Map(_ * 2) >> Collect() == [0, 2, 4]
    assert ['ab', 'cde'] >> Map(len) >> Collect() == [2, 3]
    assert [2, 3, 10] >> Map(pow, [5, 2, 3]) >> Collect() == [32, 9, 1000]


def test_Filter():
    assert [] >> Filter(_ < 5) >> Collect() == []
    assert [0, 1, 2, 3] >> Filter(_ < 2) >> Collect() == [0, 1]
    assert [0, 1, 2, 3] >> Filter(_ > 2) >> Collect() == [3]
    assert [0, 1, 2, 3] >> Filter(_ < 5) >> Collect() == [0, 1, 2, 3]
    assert [0, 1, 2, 3] >> Filter(_ < 0) >> Collect() == []


def test_FilterFalse():
    assert [] >> FilterFalse(_ < 5) >> Collect() == []
    assert [0, 1, 2, 3] >> FilterFalse(_ < 2) >> Collect() == [2, 3]
    assert [0, 1, 2, 3] >> FilterFalse(_ > 2) >> Collect() == [0, 1, 2]
    assert [0, 1, 2, 3] >> FilterFalse(_ < 5) >> Collect() == []
    assert [0, 1, 2, 3] >> FilterFalse(_ < 0) >> Collect() == [0, 1, 2, 3]


def test_Partition():
    smaller, larger = Range(5) >> Partition(_ < 3)
    assert smaller >> Collect() == [0, 1, 2]
    assert larger >> Collect() == [3, 4]

    smaller, larger = [] >> Partition(_ < 3)
    assert smaller >> Collect() == []
    assert larger >> Collect() == []

    smaller, larger = [1, 2] >> Partition(_ < 3)
    assert smaller >> Collect() == [1, 2]
    assert larger >> Collect() == []

    smaller, larger = [3, 4] >> Partition(_ < 3)
    assert smaller >> Collect() == []
    assert larger >> Collect() == [3, 4]


def test_TakeWhile():
    assert [] >> TakeWhile(_ < 2) >> Collect() == []
    assert [0, 1, 2, 3, 0] >> TakeWhile(_ < 2) >> Collect() == [0, 1]


def test_DropWhile():
    assert [] >> DropWhile(_ < 2) >> Collect() == []
    assert [0, 1, 2, 3, 0] >> DropWhile(_ < 2) >> Collect() == [2, 3, 0]


def test_Permutate():
    assert [] >> Permutate(2) >> Collect() == []
    expected = [('A', 'B'), ('A', 'C'), ('B', 'A'), ('B', 'C'), ('C', 'A'),
                ('C', 'B')]
    assert 'ABC' >> Permutate(2) >> Collect() == expected


def test_Combine():
    assert [] >> Combine(2) >> Collect() == []
    expected = [('A', 'B'), ('A', 'C'), ('B', 'C')]
    assert 'ABC' >> Combine(2) >> Collect() == expected


def test_Tee():
    it1, it2 = [1, 2, 3] >> Tee(2) >> Collect()
    assert it1 >> Collect() == [1, 2, 3]
    assert it2 >> Collect() == [1, 2, 3]


def test_If():
    assert [1, 2, 3] >> If(True, Square()) >> Collect() == [1, 4, 9]
    assert [1, 2, 3] >> If(False, Square()) >> Collect() == [1, 2, 3]
    assert [1, 2, 3] >> If(False, Take(2), Take(1)) >> Collect() == [1]


def test_Head():
    assert [] >> Head(2) == []
    assert [1] >> Head(2) == [1]
    assert [1, 2] >> Head(2) == [1, 2]
    assert [1, 2, 3] >> Head(2) == [1, 2]
    assert [1, 2, 3, 4] >> Head(2) == [1, 2]
    assert [1, 2, 3, 4] >> Head(0) == []


def test_Tail():
    assert [] >> Tail(2) == []
    assert [1] >> Tail(2) == [1]
    assert [1, 2] >> Tail(2) == [1, 2]
    assert [1, 2, 3] >> Tail(2) == [2, 3]
    assert [1, 2, 3, 4] >> Tail(2) == [3, 4]
    assert [1, 2, 3, 4] >> Tail(0) == []


def test_Drop():
    assert [] >> Drop(2) >> Collect() == []
    assert [1, 2] >> Drop(2) >> Collect() == []
    assert [1, 2, 3] >> Drop(2) >> Collect() == [3]
    assert [1, 2, 3, 4] >> Drop(2) >> Collect() == [3, 4]


def test_Pick():
    assert Range(5) >> Pick(1) >> Collect() == [0, 1, 2, 3, 4]
    assert Range(5) >> Pick(2) >> Collect() == [0, 2, 4]

    with pytest.raises(ValueError) as ex:
        [1, 2, 3] >> Pick(-1) >> Consume()
    assert str(ex.value).startswith('p_n must not be negative')

    assert Range(5) >> Pick(0.5, rnd.Random(0)) >> Collect() == [2, 3]
    assert Range(5) >> Pick(0.7, rnd.Random(0)) >> Collect() == [2, 3, 4]

    assert Range(10) >> Pick(1.0) >> Count() == 10
    assert Range(10) >> Pick(0.0) >> Count() == 0
    assert (Range(100) >> Pick(0.3) >> Collect(set)).issubset(set(range(100)))

    with pytest.raises(ValueError) as ex:
        [1, 2, 3] >> Pick(1.1) >> Consume()
    assert str(ex.value).startswith('Probability must be in [0, 1]')

    with pytest.raises(ValueError) as ex:
        [1, 2, 3] >> Pick(-0.1) >> Consume()
    assert str(ex.value).startswith('Probability must be in [0, 1]')


def test_GroupBy():
    expected = [(1, [1, 1, 1]), (2, [2]), (3, [3])]
    assert [1, 2, 1, 1, 3] >> GroupBy() >> Collect() == expected

    expected = [[1, 1, 1], [2], [3]]
    assert [1, 2, 1, 1, 3] >> GroupBy(nokey=True) >> Collect() == expected

    expected = [(2, ['--', '**']), (3, ['+++'])]
    assert ['--', '+++', '**'] >> GroupBy(len) >> Collect() == expected

    expected = [(1, [(1, 1), (1, 2)]), (2, [(2, 2)])]
    assert [(1, 1), (1, 2), (2, 2)] >> GroupBy(0) >> Collect() == expected

    expected = [(1, [(1, 1)]), (2, [(1, 2), (2, 2)])]
    assert [(1, 1), (1, 2), (2, 2)] >> GroupBy(1) >> Collect() == expected


def test_GroupBySorted():
    @nut_sink
    def KV2List(iterable):
        return iterable >> Map(lambda t: (t[0], list(t[1]))) >> Collect()

    @nut_sink
    def V2List(iterable):
        return iterable >> Map(lambda es: list(es)) >> Collect()

    expected = [(1, [1, 1, 1]), (2, [2]), (3, [3])]
    assert [1, 1, 1, 2, 3] >> GroupBySorted() >> KV2List() == expected

    expected = [[1, 1, 1], [2], [3]]
    assert [1, 1, 1, 2, 3] >> GroupBySorted(nokey=True) >> V2List() == expected

    expected = [(2, ['--', '**']), (3, ['+++'])]
    assert ['--', '**', '+++'] >> GroupBySorted(len) >> KV2List() == expected

    expected = [(1, [(1, 1), (1, 2)]), (2, [(2, 2)])]
    assert [(1, 1), (1, 2), (2, 2)] >> GroupBySorted(0) >> KV2List() == expected

    expected = [(1, [(1, 1)]), (2, [(1, 2), (2, 2)])]
    assert [(1, 1), (1, 2), (2, 2)] >> GroupBySorted(1) >> KV2List() == expected


def test_Clone():
    assert [] >> Clone(2) >> Collect() == []
    assert [] >> Clone(0) >> Collect() == []
    assert Range(4) >> Clone(0) >> Collect() == []
    assert Range(4) >> Clone(1) >> Collect() == [0, 1, 2, 3]
    assert Range(4) >> Clone(2) >> Collect() == [0, 0, 1, 1, 2, 2, 3, 3]
    assert 'abc' >> Clone(3) >> Join() == 'aaabbbccc'


def test_Shuffle():
    data = list(range(50))
    assert data >> Shuffle(100) >> Collect() != data
    assert data >> Shuffle(100) >> Collect(set) == set(data)

    assert data >> Shuffle(20) >> Collect() != data
    assert data >> Shuffle(20) >> Collect(set) == set(data)

    assert data >> Shuffle(1) >> Collect() == data

    shuffled1 = data >> Shuffle(10, rand=rnd.Random(0)) >> Collect()
    shuffled2 = data >> Shuffle(10, rand=rnd.Random(0)) >> Collect()
    assert shuffled1 == shuffled2


def test_MapCol():
    neg = lambda x: -x
    data = [(1, 2), (3, 4)]
    assert data >> MapCol(0, neg) >> Collect() == [(-1, 2), (-3, 4)]
    assert data >> MapCol(1, neg) >> Collect() == [(1, -2), (3, -4)]
    assert data >> MapCol((0, 1), neg) >> Collect() == [(-1, -2), (-3, -4)]


def test_MapMulti():
    nums, twos, greater2 = [1, 2, 3] >> MapMulti(_, _ * 2, _ > 2)
    assert nums >> Collect() == [1, 2, 3]
    assert twos >> Collect() == [2, 4, 6]
    assert greater2 >> Collect() == [False, False, True]


def test_MapPar():
    assert [-1, -2, -3] >> MapPar(abs) >> Collect() == [1, 2, 3]
    data = list(range(1000))
    assert data >> MapPar(_) >> MapPar(_) >> Collect() == data


def test_Prefetch():
    it = iter([1, 2, 3, 4])
    assert it >> Prefetch() >> Take(1) >> Collect() == [1]
    assert next(it) == 3

    it = iter([1, 2, 3, 4])
    assert it >> Prefetch() >> Take(2) >> Collect() == [1, 2]
    assert next(it) == 4


def test_Cache():
    data = [(3, 'a'), (1, 'b'), (2, 'c')]
    with Cache() as cache:
        it = iter(data)
        assert cache._dirpath is None
        assert it >> cache >> Collect() == data
        dirpath = cache._dirpath
        assert os.path.isdir(dirpath)
        assert it >> cache >> Collect() == data
    assert not os.path.isdir(dirpath)
    assert cache._dirpath is None

    with pytest.raises(ValueError) as ex:
        [1] >> Cache(storage='memory') >> Consume()
    assert str(ex.value).startswith('Unsupported storage')

    data = list(range(100))
    with Cache() as cache:
        it = iter(data)
        assert it >> cache >> Collect() == data
        assert it >> cache >> Collect() == data


def test_PrintProgress():
    with Redirect() as out:
        numbers = range(3)
        numbers >> PrintProgress(numbers, 0) >> Consume()
    expected = \
        '\rprogress: 0% \rprogress: 50% \rprogress: 100% \rprogress: 100% \n'
    assert out.getvalue() == expected


def test_Try():
    div = lambda x: int(6.0 / x)
    Div = nut_function(div)

    assert [] >> Try(div) >> Collect() == []
    assert [1, 2, 3] >> Try(div) >> Collect() == [6, 3, 2]

    with Redirect() as out:
        result = [1, 0, 3] >> Try(div, 0) >> Collect()
        assert result == [6, 0, 2]
    assert out.getvalue() == '0 : float division by zero\n'

    assert [] >> Try(Div()) >> Collect() == []
    assert [1, 2, 3] >> Try(Div()) >> Collect() == [6, 3, 2]

    with Redirect() as out:
        handler = lambda x, e: print(x, e)
        result = [1, 0, 3] >> Try(Div(), 0, handler) >> Collect()
        assert result == [6, 0, 2]
    assert out.getvalue() == '0 float division by zero\n'

    with pytest.raises(TypeError) as ex:
        [1, 0, 3] >> Try(Map(Div())) >> Collect()
    assert str(ex.value).startswith("Need (nut) function")
