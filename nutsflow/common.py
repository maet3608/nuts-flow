"""
.. module:: common
   :synopsis: Common utility functions
"""
from __future__ import print_function

import sys
import time
import random

from timeit import default_timer
from math import sqrt, log, cos, pi
from six.moves import cStringIO as StringIO


def is_iterable(obj):
    """
    Return true if object has iterator but is not a string

    :param object obj: Any object
    :return: True if object is iterable but not a string.
    :rtype: bool
    """
    return hasattr(obj, '__iter__') and not isinstance(obj, str)


def as_tuple(x):
    """
    Return x as tuple.

    If x is a single item it gets wrapped into a tuple otherwise it is
    changed to a tuple, e.g. list => tuple

    :param item or iterable x: Any item or iterable
    :return: tuple(x)
    :rtype: tuple
    """
    return tuple(x) if is_iterable(x) else (x,)


def as_list(x):
    """
    Return x as list.

    If x is a single item it gets wrapped into a list otherwise it is
    changed to a list, e.g. tuple => list

    :param item or iterable x: Any item or iterable
    :return: list(x)
    :rtype: list
    """
    return list(x) if is_iterable(x) else [x]


def as_set(x):
    """
    Return x as set.

    If x is a single item it gets wrapped into a set otherwise it is
    changed to a set, e.g. list => set

    :param item or iterable x: Any item or iterable
    :return: set(x)
    :rtype: set
    """
    return set(x) if is_iterable(x) else (x,)


def itemize(x):
    """
    Extract item from a list/tuple with only one item.

    >>> itemize([3])
    3

    >>> itemize([3, 2, 1])
    [3, 2, 1]

    >>> itemize([])
    []

    :param list|tuple x: An indexable collection
    :return: Return item in collection if there is only one, else
             returns the collection.
    :rtype: object|list|tuple
    """
    return x[0] if len(x) == 1 else x


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


def colfunc(key):
    """
    Return function that extracts element from columns.

    Used to create key functions when only column index or tuple of column
    indices is given. For instance:

    >>> data = ['a3', 'c1', 'b2']
    >>> sorted(data, key=colfunc(0))  # == sorted(data, key=lamda s:s[0])
    ['a3', 'b2', 'c1']

    >>> sorted(data, key=colfunc(1))
    ['c1', 'b2', 'a3']

    >>> list(map(colfunc((1,0)), data))
    [['3', 'a'], ['1', 'c'], ['2', 'b']]

    :param function|None key: function or None. If None the identity function
            is returned
    :return: Column extraction function.
    :rtype: function
    """
    if key is None:
        return lambda x: x
    if isinstance(key, int):
        return lambda x: x[key]
    if isinstance(key, tuple):
        return lambda x: [x[i] for i in key]
    return key


def console(*args, **kwargs):
    """
    Print to stdout and flush.

    Wrapper around Python's print function that ensures flushing after each
    call.

    >>> console('test')
    test

    :param args: Arguments
    :param kwargs: Key-Word arguments.
    """
    print(*args, **kwargs)
    sys.stdout.flush()


class Redirect(object):
    """
    Redirect stdout or stderr to string.

    >>> with Redirect() as out:
    ...     print('test')
    >>> print(out.getvalue())
    test
    <BLANKLINE>

    >>> with Redirect('STDERR') as out:
    ...     print('error', file=sys.stderr)
    >>> print(out.getvalue())
    error
    <BLANKLINE>
    """

    def __init__(self, channel='STDOUT'):
        self.channel = channel
        self.oldout = sys.stderr if channel == 'STDERR' else sys.stdout
        self.out = StringIO()
        self.__set_channel(self.out)

    def __set_channel(self, out):
        if self.channel == 'STDERR':
            sys.stderr = out
        else:
            sys.stdout = out

    def __enter__(self):
        return self.out

    def __exit__(self, *args):
        self.__set_channel(self.oldout)


# Adopted from: https://en.wikipedia.org/wiki/Mersenne_Twister
class StableRandom(random.Random):
    """A pseudo random number generator that is stable across
    Python 2.x and 3.x. Use this only for unit tests or doctests.
    This class is derived from random.Random and supports all
    methods of the base class.

    >>> rand = StableRandom(0)
    >>> rand.random()
    0.5488135024320365

    >>> rand.randint(1, 10)
    6

    >>> lst = [1, 2, 3, 4, 5]
    >>> rand.shuffle(lst)
    >>> lst
    [1, 3, 2, 5, 4]
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

    def random(self):
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

    def _randbelow(self, n, **args):
        """Return a random int in the range [0,n)"""
        return int(self.random() * n)

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
        if seed is None:
            seed = int(time.time() * 256)
        self._seed = seed

    def gauss_next(self):
        """
        Return next gaussian random number.

        :return: Random number sampled from gaussian distribution.
        :rtype: float
        """
        x1, x2 = self.random(), self.random()
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
        self.random()


class Timer(object):
    """
    A simple timer with a resolution of a second.

    .. code::

      t = Timer(fmt="Duration: %M:%S")
      time.sleep(2)  # something that takes some time, here 2 seconds
      print(t)  --> "Duration: 00:02"


    .. code::

      with Timer() as t:
          time.sleep(2)
      print(t)  --> "00:02"

    """

    def __init__(self, fmt="%M:%S"):
        """
        Creates a timer with the given time string format.

        :param str fmt: Format for time string, see `time.strftime` for details.
        """
        self.fmt = fmt
        self.start()

    def __enter__(self):
        """Enters context manager"""
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        """Exits context manager"""
        return self.stop()

    def start(self):
        """
        Starts the timer.

        Note that the construction of Timer() already starts the timer.

        :return: None
        """
        self.stime = default_timer()
        self.etime = None

    def stop(self):
        """
        Stops the timer.

        :return: None
        """
        self.etime = default_timer()

    def _gmtime(self):
        """Return current duration of timer in seconds"""
        if self.etime is None:
            self.etime = default_timer()
        delta = self.etime - self.stime
        return time.gmtime(delta)

    def __str__(self):
        """
        Returns the current timer duration as a string.

        :return: Timer duration formatted as specified by `fmt`.
        "rtype: str
        """
        return time.strftime(self.fmt, self._gmtime())
