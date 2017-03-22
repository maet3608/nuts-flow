"""
.. module:: factory
   :synopsis: Methods to construct nuts.
"""

from base import Nut, NutSink, NutSource, NutFunction


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
        def __rrshift__(self, iterable):
            args = _arg_insert(self.args, iterable, iterpos)
            return func(*args, **self.kwargs)

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
        def __rrshift__(self, iterable):
            for e in iterable:
                args = _arg_insert(self.args, e)
                if bool(func(*args, **self.kwargs)) != invert:
                    yield e

    return Wrapper


def nut_processor(func, iterpos=0):
    """
    Decorator for Nut processors.

    @nut_processor
    def Pick(iterable, p):
        for e in iterable:
            if random() > p:
                yield e

    :param function func: Function to decorate
    :param iterpos: Position of iterable in function arguments
    :return: Nut processor for given function
    :rtype: Nut
    """
    return _create_nut_wrapper(Nut, func, iterpos)


def nut_sink(func, iterpos=0):
    """
    Decorator for Nut sinks.

    @nut_sink
    def Collect(iterable, container):
        return container(iterable)

    :param function func: Function to decorate
    :param iterpos: Position of iterable in function arguments
    :return: Nut sink for given function
    :rtype: NutSink
    """
    return _create_nut_wrapper(NutSink, func, iterpos)


def nut_function(func):
    """
    Decorator for Nut functions.

    @nut_function
    def TimesN(x, n):
        return x * n

    :param function func: Function to decorate
    :return: Nut function for given function
    :rtype: NutFunction
    """

    class Wrapper(NutFunction):
        def __call__(self, element):
            return func(element, *self.args, **self.kwargs)

    return Wrapper


def nut_source(func):
    """
    Decorator for Nut sources.

    @nut_source
    def Range(start, end):
        return xrange(start, end)

    :param function func: Function to decorate
    :return: Nut source for given function
    :rtype: NutSource
    """

    class Wrapper(NutSource):
        def __iter__(self):
            return func(*self.args, **self.kwargs)

    return Wrapper


def nut_filter(func):
    """
    Decorator for Nut filters.

    @nut_filter
    def GreaterThan(x, threshold):
        return x > threshold

    :param function func: Function to decorate. Must return boolean value.
    :return: Nut filter for given function
    :rtype: Nut
    """
    return _create_filter_wrapper(func, invert=False)


def nut_filterfalse(func):
    """
    Decorator for Nut filters that are inverted.

    @nut_filterfalse
    def NotGreaterThan(x, threshold):
        return x > threshold

    :param function func: Function to decorate
    :return: Nut filter for given function. . Must return boolean value.
    :rtype: Nut
    """

    return _create_filter_wrapper(func, invert=True)
