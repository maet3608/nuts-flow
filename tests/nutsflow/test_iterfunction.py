"""
.. module:: test_iterfunction
   :synopsis: Unit tests for iterfunction module
"""

import time
import nutsflow.iterfunction as itf

from six.moves import range


def test_length():
    assert itf.length(range(10)) == 10
    assert itf.length([]) == 0


def test_interleave():
    it1 = [1, 2]
    it2 = 'abc'
    it = itf.interleave(it1, it2)
    assert list(it) == [1, 'a', 2, 'b', 'c']
    assert list(itf.interleave([], [])) == []
    assert list(itf.interleave('12', [])) == ['1', '2']


def test_take():
    it = itf.take(range(10), 3)
    assert list(it) == [0, 1, 2]
    it = itf.take(range(10), 0)
    assert list(it) == []
    it = itf.take(range(0), 3)
    assert list(it) == []


def test_nth():
    assert itf.nth(range(10), 2) == 2
    assert itf.nth(range(10), 100) is None
    assert itf.nth(range(10), 100, -1) == -1


def test_unique():
    assert list(itf.unique([1, 2, 3])) == [1, 2, 3]
    assert list(itf.unique([2, 3, 1, 1, 2, 4])) == [2, 3, 1, 4]
    assert list(itf.unique([])) == []

    data = [(1, 'a'), (2, 'a'), (3, 'b')]
    it = itf.unique(data, key=lambda t: t[1])
    assert list(it) == [(1, 'a'), (3, 'b')]


def test_chunked():
    it = itf.chunked(range(5), 2)
    assert list(map(tuple, it)) == [(0, 1), (2, 3), (4,)]
    it = itf.chunked(range(6), 3)
    assert list(map(tuple, it)) == [(0, 1, 2), (3, 4, 5)]
    assert list(itf.chunked([], 2)) == []


def test_consume():
    it = iter(range(10))
    itf.consume(it)
    assert next(it, None) is None
    it = iter(range(10))
    itf.consume(it, 5)
    assert next(it, None) == 5


def test_flatten():
    assert list(itf.flatten([])) == []
    iterable = [(1, 2), (3, 4, 5)]
    assert list(itf.flatten(iterable)) == [1, 2, 3, 4, 5]


def test_flatmap():
    f = lambda n: str(n) * n
    it = itf.flatmap(f, [1, 2, 3])
    assert list(it) == ['1', '2', '2', '3', '3', '3']
    it = itf.flatmap(f, [])
    assert list(it) == []


def test_partition():
    pred = lambda x: x < 6
    smaller, larger = itf.partition(range(10), pred)
    assert list(smaller) == [0, 1, 2, 3, 4, 5]
    assert list(larger) == [6, 7, 8, 9]


def test_prefetch_iterator():
    def sleep():
        time.sleep(0.01)

    def number_generator():
        for i in range(10):
            sleep()
            yield i

    start = time.time()
    for _ in number_generator():
        sleep()
    duration1 = time.time() - start

    start = time.time()
    for _ in itf.PrefetchIterator(number_generator()):
        sleep()
    duration2 = time.time() - start

    assert duration2 < duration1
