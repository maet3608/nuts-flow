"""
.. module:: test_common
   :synopsis: Unit tests for common module
"""

from __future__ import print_function

import sys
import time

import numpy as np

from pytest import approx
from time import sleep
from collections import namedtuple
from nutsflow import MeanStd
from nutsflow.common import (sec_to_hms, timestr, Redirect, as_tuple, as_set,
                             as_list, is_iterable, istensor, stype, shapestr,
                             isnan, colfunc, console, itemize, StableRandom,
                             Timer)


def test_isnan():
    assert not isnan(1)
    assert not isnan(0)
    assert isnan(np.NaN)


def test_is_iterable():
    assert is_iterable([1, 2])
    assert not is_iterable('12')


def test_istensor():
    assert istensor(np.zeros((2, 3)))
    assert not istensor([1, 2])


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


def test_itemize():
    assert itemize([]) == []
    assert itemize([3]) == 3
    assert itemize([3, 2, 1]) == [3, 2, 1]


def test_sec_to_hms():
    assert sec_to_hms('80') == (0, 1, 20)
    assert sec_to_hms(3 * 60 * 60 + 2 * 60 + 1) == (3, 2, 1)


def test_timestr():
    assert timestr('') == ''
    assert timestr('80') == '0:01:20'


def test_shapestr():
    assert shapestr(np.array([1, 2])) == '2'
    assert shapestr(np.zeros((3, 4))) == '3x4'
    assert shapestr(np.zeros((3, 4), dtype='uint8'), True) == '3x4:uint8'


def test_stype():
    a = np.zeros((3, 4), dtype='uint8')
    b = np.zeros((1, 2), dtype='float32')
    assert stype(1.1) == '<float> 1.1'
    assert stype([1, 2]) == '[<int> 1, <int> 2]'
    assert stype((1, 2)) == '(<int> 1, <int> 2)'
    assert stype({1, 2}) == '{<int> 1, <int> 2}'
    assert stype([1, (2, 3.1)]) == '[<int> 1, (<int> 2, <float> 3.1)]'
    assert stype(a) == '<ndarray> 3x4:uint8'
    assert stype(b) == '<ndarray> 1x2:float32'
    expect = '[<ndarray> 3x4:uint8, [<ndarray> 1x2:float32]]'
    assert stype([a, [b]]) == expect
    expect = '[[<ndarray> 3x4:uint8], [<ndarray> 1x2:float32]]'
    assert stype([[a], [b]]) == expect
    expect = '{a:<ndarray> 3x4:uint8, b:<ndarray> 1x2:float32}'
    assert stype({'a': a, 'b': b}) == expect
    Sample = namedtuple('Sample', 'x,y')
    expect = 'Sample(x=<ndarray> 3x4:uint8, y=<int> 1)'
    assert stype(Sample(a, 1)) == expect


def test_colfunc():
    data = ['a3', 'b2', 'c1']
    assert list(map(colfunc(None), data)) == data
    assert list(map(colfunc(0), data)) == ['a', 'b', 'c']
    assert list(map(colfunc(1), data)) == ['3', '2', '1']
    expected = [['3', 'a'], ['2', 'b'], ['1', 'c']]
    assert list(map(colfunc((1, 0)), data)) == expected


def test_console():
    with Redirect() as out:
        console('test')
    assert out.getvalue() == 'test\n'


def test_Redirect():
    with Redirect() as out:
        print('test')
    assert out.getvalue() == 'test\n'

    with Redirect('STDERR') as out:
        print('error', file=sys.stderr)
    assert out.getvalue() == 'error\n'


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

    rnd = StableRandom()
    numbers = [rnd._randbelow(10) for _ in range(1000)]
    assert max(numbers) < 10
    assert min(numbers) >= 0

    rnd = StableRandom()
    numbers = [rnd.gauss_next() for _ in range(10000)]
    my, std = numbers >> MeanStd()
    assert 0.0 == approx(my, abs=0.1)
    assert 1.0 == approx(std, abs=0.1)


def test_timer():
    t = Timer()
    time.sleep(1.3)
    assert str(t) == '00:01'

    with Timer() as t:
        time.sleep(1.3)
    assert str(t) == '00:01'

    t = Timer()
    time.sleep(0.5)
    t.start()
    time.sleep(1.3)
    t.stop()
    time.sleep(0.5)
    assert str(t) == '00:01'
