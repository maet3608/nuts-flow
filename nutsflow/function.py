"""
.. module:: function
   :synopsis: Nuts that perform functions on single stream elements.
"""
from __future__ import print_function
from __future__ import absolute_import

import time
import threading

from .common import console
from .factory import nut_function, NutFunction


@nut_function
def Identity(x):
    """
    iterable >> Identity()

    Return same input as console.

    >>> from nutsflow import Collect
    >>> [1, 2, 3] >> Identity() >> Collect()
    [1, 2, 3]

    :param iterable iterable: Any iterable
    :param any x: Any input
    :return: Returns input unaltered
    :rtype: object
    """
    return x


@nut_function
def Square(x):
    """
    iterable >> Square()

    Return squared input.

    >>> from nutsflow import Collect
    >>> [1, 2, 3] >> Square() >> Collect()
    [1, 4, 9]

    :param iterable iterable: Any iterable over numbers
    :param number x: Any number
    :return: Squared number
    :rtype: number
    """
    return x * x


@nut_function
def NOP(x, *args):  # *args is needed!
    """
    iterable >> Nop(*args)

    No Operation. Useful to skip nuts. Same as commenting a nut out
    or removing it from a pipeline.

    >>> from nutsflow import Collect
    >>> [1, 2, 3] >> NOP(Square()) >> Collect()
    [1, 2, 3]

    :param iterable iterable: Any iterable
    :param object x: Any object
    :param args args: Additional args are ignored.
    :return: Squared number
    :rtype: number
    """
    return x


@nut_function
def Get(x, start, end=None, step=None):
    """
    iterable >> Get(start, end, step)

    Extract elements from x. Equivalent to Python slicing [start:end:step]
    but per element of the iterable.

    >>> from nutsflow import Collect

    >>> [(1, 2, 3), (4, 5, 6)] >> Get(1) >> Collect()
    [2, 5]

    >>> [(1, 2, 3), (4, 5, 6)] >> Get(0, 2) >> Collect()
    [(1, 2), (4, 5)]

    >>> [(1, 2, 3), (4, 5, 6)] >> Get(0, 3, 2) >> Collect()
    [(1, 3), (4, 6)]

    >>> [(1, 2, 3), (4, 5, 6)] >> Get(None) >> Collect()
    [(1, 2, 3), (4, 5, 6)]

    :param iterable iterable: Any iterable
    :param indexable x: Any indexable input
    :param int start: Start index for columns to extract from x
           If start = None, x is returned
    :param int end: End index (not inclusive)
    :param int step: Step index (same as slicing)
    :return: Extracted elements
    :rtype: object|list
    """
    return x if start is None else x[slice(start, end, step) if end else start]


@nut_function
def GetCols(x, *columns):
    """
    iterable >> GetCols(*columns)

    Extract elements in given order from x. Also useful to change the order of
    or clone elements in x.

    >>> from nutsflow import Collect
    
    >>> [(1, 2, 3), (4, 5, 6)] >> GetCols(1) >> Collect()
    [(2,), (5,)]

    >>> [[1, 2, 3], [4, 5, 6]] >> GetCols(2, 0) >> Collect()
    [(3, 1), (6, 4)]

    >>> [(1, 2, 3), (4, 5, 6)] >> GetCols(2, 1, 0) >> Collect()
    [(3, 2, 1), (6, 5, 4)]

    >>> [(1, 2, 3), (4, 5, 6)] >> GetCols(1, 1) >> Collect()
    [(2, 2), (5, 5)]

    :param iterable iterable: Any iterable
    :param indexable container x: Any indexable input
    :param int|tuple columns: Indicies of elements/columns in x to extract
    :return: Extracted elements
    :rtype: tuple
    """
    return tuple(x[i] for i in columns)


class Counter(NutFunction):
    """
    Increment counter depending on elements in iterable.
    Intended mostly for debugging and monitoring. Avoid for standard
    processing of data. The function has side-effects but is thread-safe.
    """

    def __init__(self, name, filterfunc=lambda x: True, value=0):
        """
        counter = Counter(name, filterfunc, value)
        iterable >> counter

        >>> from nutsflow import Consume
        >>> counter = Counter('smallerthan3', lambda x: x < 3, 1)
        >>> range(10) >> counter >> Consume()
        >>> counter
        smallerthan3 = 4

        :param str name: Name of the counter
        :param func filterfunc: Filter function.
        :param int value: Initial value
           Count only elements where func returns True.
        """
        self.name = name
        self.value = value
        self.filterfunc = filterfunc
        self.lock = threading.Lock()

    def reset(self, value=0):
        """
        Reset counter to given value.

        :param int value: Reset value
        """
        with self.lock:
            self.value = value

    def __repr__(self):
        """
        Return counter value as string.
        :return: Counter value
        :rtype: str
        """
        return self.__str__()

    def __str__(self):
        """
        Return string representation of counter value.

        :return: counter name and value as string
        :rtype: str
        """
        return '{} = {}'.format(self.name, self.value)

    def __call__(self, x):
        """
        Increment counter.

        :param object x: Element in iterable
        :return: Unchanged element
        :rtype: Any
        """
        with self.lock:
            if self.filterfunc(x):
                self.value += 1
        return x


@nut_function
def Sleep(x, duration=1):
    """
    iterable >> Sleep(duration)

    Return same input as console but sleep for each element.

    >>> from nutsflow import Collect
    >>> [1, 2, 3] >> Sleep(0.1) >> Collect()
    [1, 2, 3]

    :param iterable iterable: Any iterable
    :param object x: Any input
    :param float duration: Sleeping time in seconds.
    :return: Returns input unaltered
    :rtype: object
    """
    time.sleep(duration)
    return x


@nut_function
def Format(x, fmt):
    """
    iterable >> Format(fmt)

    Return input as formatted string. For format definition see:
    https://docs.python.org/2/library/string.html

    >>> from nutsflow import Collect
    >>> [1, 2, 3] >> Format('num:{}') >> Collect()
    ['num:1', 'num:2', 'num:3']

    >>> [(1, 2), (3, 4)] >> Format('{0}:{1}') >> Collect()
    ['1:2', '3:4']

    :param iterable iterable: Any iterable
    :param string fmt: Formatting string, e.g. '{:02d}'
    :return: Returns inputs as strings formatted as specified
    :rtype: str
    """
    return fmt.format(*(x if hasattr(x, '__iter__') else [x]))


class Print(NutFunction):
    """
    Print elements in iterable.
    """

    def __init__(self, fmtfunc=None, every_sec=0, every_n=0,
                 filterfunc=lambda x: True):
        """
        iterable >> Print(fmtfunc=None, every_sec=0, every_n=0,
                          filterfunc=lambda x: True)

        Return same input as console but print for each element.

        >>> from nutsflow import Consume
        >>> [1, 2] >> Print() >> Consume()
        1
        2

        >>> range(10) >> Print(every_n=3) >> Consume()
        2
        5
        8

        >>> even = lambda x: x % 2 == 0
        >>> [1, 2, 3, 4] >> Print(filterfunc=even) >> Consume()
        2
        4

        >>> [[1, 2], [3, 4]] >> Print('number={1}:{0}') >> Consume()
        number=2:1
        number=4:3

        >>> myfmt = lambda x: 'char='+x.upper()
        >>> ['a', 'b'] >> Print(myfmt) >> Consume()
        char=A
        char=B

        :param object x: Any input

        :param string|function fmtfunc: Format string or function.
                fmtfunc is a standard Python str.format() string,
                see https://docs.python.org/2/library/string.html
                or a function that returns a string.
        :param float every_sec: Print every given second, e.g. to print
                every 2.5 sec every_sec = 2.5
        :param int every_n: Print every n-th call.
        :param function filterfunc: Boolean function to filter print.
        :return: Returns input unaltered
        :rtype: object
        :raise: ValueError if fmtfunc is not string or function
        """
        self.fmtfunc = fmtfunc
        self.every_sec = every_sec
        self.every_n = every_n
        self.filterfunc = filterfunc
        self.cnt = 0
        self.time = time.time()

    def __delta_sec(self):
        """Return time in seconds (float) consumed between prints so far"""
        return time.time() - self.time

    def __should_print(self, x):
        """Return true if element x should be printed"""
        self.cnt += 1
        return (self.filterfunc(x) and
                self.cnt >= self.every_n and
                self.__delta_sec() >= self.every_sec)

    def __call__(self, x):
        """Return element x and potentially print its value"""
        if not self.__should_print(x):
            return x

        self.cnt = 0  # reset counter
        self.time = time.time()  # reset timer

        fmtfunc = self.fmtfunc
        if hasattr(x, 'ndim'):  # is it a numpy array?
            x = x.tolist() if x.ndim else x.item()
        if not fmtfunc:
            console(x)
        elif isinstance(fmtfunc, str):
            console(fmtfunc.format(*(x if hasattr(x, '__iter__') else [x])))
        elif hasattr(fmtfunc, '__call__'):
            console(fmtfunc(x))
        else:
            raise ValueError('Invalid format ' + str(fmtfunc))

        return x
