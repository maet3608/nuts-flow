"""
.. module:: test underscore
   :synopsis: Unit tests for underscore module
"""

from __future__ import division

from nutsflow.underscore import _wrap, _


def test_wrap():
    def f(first, second):
        return first + second

    assert f('1', '2') == '12'
    assert _wrap(f, '1')('2') == '21'


def test_underscore():
    assert (_ + 1)(2) == 3
    assert (1 + _)(2) == 3
    assert (_ - 1)(2) == 1
    assert (1 - _)(2) == -1
    assert (_ * 2)(4) == 8
    assert (2 * _)(4) == 8
    assert (_ / 2)(4) == 2
    assert (4 / _)(2) == 2
    assert (_ % 2)(5) == 1
    assert (5 % _)(2) == 1

    assert (_ == 1)(1)
    assert not (_ == 1)(2)
    assert (_ != 1)(2)
    assert not (_ != 1)(1)
    assert (_ > 1)(2)
    assert (_ >= 1)(2)
    assert (_ >= 2)(2)
    assert (_ < 2)(1)
    assert (_ <= 2)(1)
    assert (_ <= 2)(2)

    assert (_[1])([0, 1, 2]) == 1
    assert (_[1:3])([0, 1, 2, 4]) == [1, 2]
