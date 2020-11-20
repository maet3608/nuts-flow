"""
.. module:: factory
   :synopsis: Functions and decorators to construct nuts.
"""
from __future__ import absolute_import

from nutsflow.base import Nut, NutSink, NutSource, NutFunction


def _arg_insert(args, arg, pos=0):
    """
    Insert arg in args a given position.

    :param tuple args: Some function arguments
    :param any arg: Some function argument
    :param int pos: Insert position. If None argument is appended.
    :return: List with arguments where arg is inserted
    :rtype: list
    """
    args = list(args)
    if pos is None:
        args.append(arg)
    else:
        args.insert(pos, arg)
    return args


def _create_nut_wrapper(base_class, func, iterpos):
    """
    Return Nut for given function.

    :param class base_class: Base class, e.g. Nut, NutSink, NutFunction, ...
    :param function func: Function to wrap
    :param int iterpos: Argument position for iterable in function.
    :return: Nut that wraps the given function.
    :rtype: Nut
    """

    class Wrapper(base_class):
        __doc__ = func.__doc__

        def __rrshift__(self, iterable):
            args = _arg_insert(self.args, iterable, iterpos)
            return func(*args, **self.kwargs)

    Wrapper.__name__ = func.__name__
    Wrapper.__module__ = func.__module__
    Wrapper.__rrshift__.__doc__ = ""
    return Wrapper


def _create_filter_wrapper(func, invert=False):
    """
    Return filter Nut for given function.

    :param func: Filter function to wrap
    :param invert: Filter is inverted.
    :return: Nut operates as a filter.
    :rtype: Nut
    """

    class Wrapper(Nut):
        __doc__ = func.__doc__

        def __rrshift__(self, iterable):
            for e in iterable:
                args = _arg_insert(self.args, e)
                if bool(func(*args, **self.kwargs)) != invert:
                    yield e

    Wrapper.__name__ = func.__name__
    Wrapper.__module__ = func.__module__
    Wrapper.__rrshift__.__doc__ = ""
    return Wrapper


def nut_function(func):
    """
    Decorator for Nut functions.

    Example on how to define a custom function nut:

    .. code::

      @nut_function
      def TimesN(x, n):
          return x * n

      [1, 2, 3] >> TimesN(2) >> Collect()  -->  [2, 4, 6]

    :param function func: Function to decorate
    :return: Nut function for given function
    :rtype: NutFunction
    """

    class Wrapper(NutFunction):
        __doc__ = func.__doc__

        def __call__(self, element):
            return func(element, *self.args, **self.kwargs)

    Wrapper.__name__ = func.__name__
    Wrapper.__module__ = func.__module__
    Wrapper.__call__.__doc__ = ""
    return Wrapper


def nut_source(func):
    """
    Decorator for Nut sources.

    Example on how to define a custom source nut. Note that a source
    must return an iterable/generator and does not read any input.

    .. code::

      @nut_source
      def MyRange(start, end):
          return range(start, end)

      MyRange(0, 5) >> Collect()  --> [0, 1, 2, 3, 4]


    .. code::

      @nut_source
      def MyRange2(start, end):
          for i in range(start, end):
              yield i * 2

      MyRange2(0, 5) >> Collect()  --> [0, 2, 4, 6, 8]

    :param function func: Function to decorate
    :return: Nut source for given function
    :rtype: NutSource
    """

    class Wrapper(NutSource):
        __doc__ = func.__doc__

        def __iter__(self):
            return func(*self.args, **self.kwargs)

    Wrapper.__name__ = func.__name__
    Wrapper.__module__ = func.__module__
    return Wrapper


def nut_processor(func, iterpos=0):
    """
    Decorator for Nut processors.

    Examples on how to define a custom processor nut.
    Note that a processor reads an iterable and must return
    an iterable/generator

    .. code::

      @nut_processor
      def Twice(iterable):
          for e in iterable:
              yield e
              yield e

      [1, 2, 3] >> Twice() >> Collect()  --> [1, 1, 2, 2, 3, 3]


    .. code::

      @nut_processor
      def Odd(iterable):
          return (e for e in iterable if e % 2)

      [1, 2, 3, 4, 5] >> Odd() >> Collect()  --> [1, 3, 5]


    .. code::

      @nut_processor
      def Clone(iterable, n):
          for e in iterable:
              for _ in range(p):
                  yield e

      [1, 2, 3] >> Clone(2) >> Collect()  --> [1, 1, 2, 2, 3, 3]

    :param function func: Function to decorate
    :param iterpos: Position of iterable in function arguments
    :return: Nut processor for given function
    :rtype: Nut
    """
    return _create_nut_wrapper(Nut, func, iterpos)


def nut_sink(func, iterpos=0):
    """
    Decorator for Nut sinks.

    Example on how to define a custom sink nut:

    .. code::

      @nut_sink
      def ToList(iterable):
          return list(iterable)

      range(5) >> ToList()  -->   [0, 1, 2, 3, 4]


    .. code::

      @nut_sink
      def MyCollect(iterable, container):
          return container(iterable)

      range(5) >> MyCollect(tuple)  -->   (0, 1, 2, 3, 4)


    .. code::

      @nut_sink
      def MyProd(iterable):
          p = 1
          for e in iterable:
              p *= e
          return p

      [1, 2, 3] >> MyProd()  --> 12


    :param function func: Function to decorate
    :param iterpos: Position of iterable in function arguments
    :return: Nut sink for given function
    :rtype: NutSink
    """
    return _create_nut_wrapper(NutSink, func, iterpos)


def nut_filter(func):
    """
    Decorator for Nut filters.

    Also see nut_filerfalse().
    Example on how to define a custom filter nut:

    .. code::

      @nut_filter
      def Positive(x):
          return x > 0

      [-1, 1, -2, 2] >> Positive() >> Collect()  --> [1, 2]


    .. code::

      @nut_filter
      def GreaterThan(x, threshold):
          return x > threshold

      [1, 2, 3, 4] >> GreaterThan(2) >> Collect()  --> [3, 4] 

    :param function func: Function to decorate. Must return boolean value.
    :return: Nut filter for given function
    :rtype: Nut
    """
    return _create_filter_wrapper(func, invert=False)


def nut_filterfalse(func):
    """
    Decorator for Nut filters that are inverted.

    Also see nut_filter().
    Example on how to define a custom filter-false nut:

    .. code::

      @nut_filterfalse
      def NotGreaterThan(x, threshold):
          return x > threshold

      [1, 2, 3, 4] >> NotGreaterThan(2) >> Collect()  --> [1, 2]

    :param function func: Function to decorate
    :return: Nut filter for given function. . Must return boolean value.
    :rtype: Nut
    """

    return _create_filter_wrapper(func, invert=True)
