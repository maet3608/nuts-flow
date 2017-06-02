"""
.. module:: factory
   :synopsis: Unit tests for factory module
"""

from six.moves import range 
from nutsflow.base import Nut
from nutsflow.sink import Collect
from nutsflow.factory import (_arg_insert, _create_nut_wrapper,
                              _create_filter_wrapper, nut_processor, nut_sink,
                              nut_function, nut_source, nut_filter,
                              nut_filterfalse)


def test_arg_insert():
    args = (1, 2)
    assert _arg_insert(args, 'a') == ['a', 1, 2]
    assert _arg_insert(args, 'a', 1) == [1, 'a', 2]
    assert _arg_insert(args, 'a', 3) == [1, 2, 'a']
    assert _arg_insert(args, 'a', None) == [1, 2, 'a']


def test_create_nut_wrapper():
    func = lambda iterable, arg1, arg2: (iterable, arg1, arg2)
    wrapper = _create_nut_wrapper(Nut, func, 0)
    assert isinstance(wrapper(), Nut)
    assert ['a'] >> wrapper(2, 3) >> Collect() == [['a'], 2, 3]


def test_create_filter_wrapper():
    greaterThan = lambda x, t: x > t
    wrapper = _create_filter_wrapper(greaterThan)
    assert isinstance(wrapper(), Nut)
    assert [1, 2, 3, 4] >> wrapper(2) >> Collect() == [3, 4]

    wrapper = _create_filter_wrapper(greaterThan, True)
    assert [1, 2, 3, 4] >> wrapper(2) >> Collect() == [1, 2]

    not_empty = lambda x: x
    wrapper = _create_filter_wrapper(not_empty)
    assert [[1], [], [3], []] >> wrapper() >> Collect() == [[1], [3]]
    assert [1, 0, 3, 0] >> wrapper() >> Collect() == [1, 3]
    assert [1, [], [3], []] >> wrapper() >> Collect() == [1, [3]]


def test_nut_processor():
    @nut_processor
    def CloneN(iterable, n):
        for e in iterable:
            for _ in range(n):
                yield e

    assert [1, 2] >> CloneN(2) >> Collect() == [1, 1, 2, 2]


def test_nut_sink():
    @nut_sink
    def MyCollect(iterable, container):
        return container(iterable)

    assert [1, 2, 2] >> MyCollect(set) == {1, 2}


def test_nut_function():
    @nut_function
    def TimesN(x, n):
        return x * n

    assert [1, 2] >> TimesN(2) >> Collect() == [2, 4]


def test_nut_source():
    @nut_source
    def MyRange(start, end):
        return iter(range(start, end))

    assert MyRange(1, 4) >> Collect() == [1, 2, 3]


def test_nut_filter():
    @nut_filter
    def GreaterThan(x, threshold):
        return x > threshold

    assert [1, 2, 3, 4] >> GreaterThan(2) >> Collect() == [3, 4]


def test_nut_filterfalse():
    @nut_filterfalse
    def NotGreaterThan(x, threshold):
        return x > threshold

    assert [1, 2, 3, 4] >> NotGreaterThan(2) >> Collect() == [1, 2]
