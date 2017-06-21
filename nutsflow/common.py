"""
.. module:: common
   :synopsis: Common utility functions
"""
from __future__ import print_function

import sys

import random as rnd

from math import sqrt, log, cos, pi
from six.moves import cStringIO as StringIO


def as_tuple(x):
    """
    Return x as tuple.

    If x is a single item it gets wrapped into a tuple otherwise it is
    changed to a tuple, e.g. list => tuple

    :param item or iterable x: Any item or iterable
    :return: tuple(x)
    :rtype: tuple
    """
    return tuple(x) if hasattr(x, '__iter__') else (x,)


def as_list(x):
    """
    Return x as list.

    If x is a single item it gets wrapped into a list otherwise it is
    changed to a list, e.g. tuple => list

    :param item or iterable x: Any item or iterable
    :return: list(x)
    :rtype: list
    """
    return list(x) if hasattr(x, '__iter__') else [x]


def as_set(x):
    """
    Return x as set.

    If x is a single item it gets wrapped into a set otherwise it is
    changed to a set, e.g. list => set

    :param item or iterable x: Any item or iterable
    :return: set(x)
    :rtype: set
    """
    return set(x) if hasattr(x, '__iter__') else (x,)


def sec_to_hms(duration):
    """
    Return hours, minutes and seconds for given duration.

    >>> sec_to_hms('80')
    (0, 1, 20)

    :param int|str duration: Duration in seconds. Can be int or string.
    :return: tuple (hours, minutes, seconds)
    :rtype: (int, int, int)
    """
    s = int(duration)
    h = s // 3600
    s -= (h * 3600)
    m = s // 60
    s -= (m * 60)
    return h, m, s


def timestr(duration, fmt='{:d}:{:02d}:{:02d}'):
    """
    Return duration as formatted time string or empty string if no duration

    >>> timestr('80')
    '0:01:20'

    :param int|str duration: Duration in seconds. Can be int or string.
    :param str: Format for string, e.g. '{:d}:{:02d}:{:02d}'
    :return: duration as formatted time, e.g. '0:01:20' or '' if duration
       shorter than one second.
    :rtype: string
    """
    if not duration:
        return ''
    h, m, s = sec_to_hms(duration)
    return fmt.format(h, m, s)


def console(*args, **kwargs):
    """
    Print to stdout and flush.

    Wrapper around Python's print function that ensures flushing after each
    call.

    >>> print('test')
    test

    :param args: Arguments
    :param kwargs: Key-Word arguments.
    """
    print(*args, **kwargs)
    sys.stdout.flush()


class Redirect(object):
    """
    Redirect stdout to string.

    >>> with Redirect() as out:
    ...     print('test')
    >>> print(out.getvalue())
    test
    <BLANKLINE>
    """

    def __init__(self):
        self.oldstdout = sys.stdout
        self.stdout = StringIO()
        sys.stdout = self.stdout

    def __enter__(self):
        return self.stdout

    def __exit__(self, *args):
        sys.stdout = self.oldstdout


# Adopted from: https://en.wikipedia.org/wiki/Mersenne_Twister
class StableRandom(rnd.Random):
    """A pseudo random number generator that is stable across
    Python 2.x and 3.x. Use this only for unit tests or doctests.
    This class is derived from random.Random and supports all
    methods of the base class.

    >>> rand = StableRandom(0)
    >>> rand.gauss_next()
    -0.9142740968041003

    >>> rand.randint(1, 10)
    9

    >>> lst = [1, 2, 3, 4, 5]
    >>> rand.shuffle(lst)
    >>> lst
    [3, 5, 1, 2, 4]
    """

    def __init__(self, seed=None):
        """
        Initialize random number generator.

        :param None|int seed: Seed. If None the system time is used.
        """
        self.seed(seed)
        self.index = 624
        self.mt = [0] * 624
        self.mt[0] = self._seed
        for i in range(1, 624):
            self.mt[i] = self._int32(
                1812433253 * (self.mt[i - 1] ^ self.mt[i - 1] >> 30) + i)

    def _int32(self, x):
        """Return the 32 least significant bits"""
        return int(0xFFFFFFFF & x)

    def _next_rand(self):
        """Return next random number in [0,1["""
        if self.index >= 624:
            self._twist()

        y = self.mt[self.index]
        y = y ^ y >> 11
        y = y ^ y << 7 & 2636928640
        y = y ^ y << 15 & 4022730752
        y = y ^ y >> 18

        self.index = self.index + 1

        return float(self._int32(y)) / 0xffffffff

    def _twist(self):
        """Mersenne Twister"""
        for i in range(624):
            y = self._int32((self.mt[i] & 0x80000000) +
                            (self.mt[(i + 1) % 624] & 0x7fffffff))
            self.mt[i] = self.mt[(i + 397) % 624] ^ y >> 1

            if y % 2 != 0:
                self.mt[i] = self.mt[i] ^ 0x9908b0df
        self.index = 0

    def seed(self, seed=None):
        """
        Set seed.

        :param None|int seed: Seed. If None the system time is used.
        """
        import time
        if seed is None:
            seed = int(time.time() * 256)
        self._seed = seed

    def gauss_next(self):
        """
        Return next gaussian random number.

        :return: Random number sampled from gaussian distribution.
        :rtype: float
        """
        x1, x2 = self._next_rand(), self._next_rand()
        return sqrt(-2.0 * log(x1 + 1e-10)) * cos(2.0 * pi * x2)

    def getstate(self):
        """
        Return state of generator.

        :return: Index and Mersenne Twister array.
        :rtype: tuple
        """
        return self.mt[:], self.index

    def setstate(self, state):
        """
        Set state of generator.

        :param tuple state: State to set as produced by getstate()
        """
        self.mt, self.index = state

    def jumpahead(self, n):
        """
        Set state of generator far away from current state.

        :param int n: Distance to jump.
        """
        self.index += n
        self._next_rand()
