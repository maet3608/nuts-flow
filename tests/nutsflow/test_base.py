"""
.. module:: test_base
   :synopsis: Unit tests for base module
"""

import pytest
from nutsflow.base import Nut, NutFunction, NutSource, NutSink


def test_Nut():
    nut = Nut(1, 2, num=3)
    assert nut.args == (1, 2)
    assert nut.kwargs == {'num': 3}

    with pytest.raises(NotImplementedError) as ex:
        [1, 2] >> nut
    assert str(ex.value).startswith('Needs to implement  __rrshift__')

    class Ident(Nut):
        def __rrshift__(self, iterable):
            return iterable

    assert Ident()([1, 2]) == [1, 2]


def test_NutFunction():
    func = NutFunction()

    with pytest.raises(NotImplementedError) as ex:
        func(1)
    assert str(ex.value).startswith('Needs to implement  __call__()')

    class Identity(NutFunction):
        def __call__(self, element):
            return element

    assert list([1, 2] >> Identity()) == [1, 2]


def test_NutSource():
    source = NutSource()

    with pytest.raises(SyntaxError) as ex:
        [1, 2] >> source
    assert str(ex.value).startswith("Sources don't have inputs")

    with pytest.raises(NotImplementedError) as ex:
        for _ in source:
            pass
    assert str(ex.value).startswith("Needs to implement __iter__()")


def test_NutSink():
    sink = NutSink()

    with pytest.raises(SyntaxError) as ex:
        for _ in sink:
            pass
    assert str(ex.value).startswith("Sinks cannot be inputs:")

    class Len(NutSink):
        def __rrshift__(self, iterable):
            return len(list(iterable))

    assert [1, 2, 3] >> Len() == 3
    assert Len()([1, 2, 3]) == 3  # Sink can operate as function
    assert list(map(Len(), ['a', 'bb', 'cc'])) == [1, 2, 2]
