"""
.. module:: test_common
   :synopsis: Unit tests for common module
"""

from __future__ import print_function

from pytest import approx
from time import sleep
from nutsflow.common import (sec_to_hms, timestr, Redirect, as_tuple, as_set,
                             as_list, console, StableRandom)


def test_as_tuple():
    assert as_tuple(1) == (1,)
    assert as_tuple((1, 2)) == (1, 2)
    assert as_tuple([1, 2]) == (1, 2)


def test_as_list():
    assert as_list(1) == [1]
    assert as_list((1, 2)) == [1, 2]
    assert as_list([1, 2]) == [1, 2]


def test_as_set():
    assert as_set(1) == (1,)
    assert as_set((1, 2)) == {1, 2}
    assert as_set([1, 2]) == {1, 2}


def test_sec_to_hms():
    assert sec_to_hms('80') == (0, 1, 20)
    assert sec_to_hms(3 * 60 * 60 + 2 * 60 + 1) == (3, 2, 1)


def test_timestr():
    assert timestr('') == ''
    assert timestr('80') == '0:01:20'


def test_output():
    with Redirect() as out:
        console('test')
    assert out.getvalue() == 'test\n'


def test_Redirect():
    with Redirect() as out:
        print('test')
    assert out.getvalue() == 'test\n'


def test_StableRandom():
    rnd = StableRandom(1)
    assert rnd.randint(1, 10) == 5
    assert rnd.uniform(-10, 10) == approx(9.943696167306904)
    assert rnd.random() == approx(0.7203244894557457)
    assert rnd.sample(range(10), 3) == [9, 0, 1]

    lst = [1, 2, 3, 4, 5]
    rnd.shuffle(lst)
    assert lst == [5, 3, 1, 4, 2]

    rnd = StableRandom()
    assert max(rnd.random() for _ in range(1000)) < 1.0
    assert min(rnd.random() for _ in range(1000)) >= 0.0

    rnd1, rnd2 = StableRandom(0), StableRandom(0)
    for _ in range(100):
        assert rnd1.random() == rnd2.random()

    rnd1, rnd2 = StableRandom(0), StableRandom(0)
    rnd2.jumpahead(10)
    for _ in range(100):
        assert rnd1.random() != rnd2.random()
    rnd2.setstate(rnd1.getstate())
    for _ in range(100):
        assert rnd1.random() == rnd2.random()

    rnd1, rnd2 = StableRandom(0), StableRandom(1)
    for _ in range(100):
        assert rnd1.random() != rnd2.random()

    rnd1 = StableRandom()
    sleep(0.5)  # seed is based on system time.
    rnd2 = StableRandom()
    for _ in range(100):
        assert rnd1.random() != rnd2.random()
