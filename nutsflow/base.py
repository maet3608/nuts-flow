"""
.. module:: base
   :synopsis: Base classes and functions.
"""

from six.moves import map


class Nut(object):
    """
    Base class for all Nuts. Iterables or functions wrapped in Nuts can be
    chained using the '>>' operator. The aim is code with an explicit
    data flow. See the following example using Python iterators versus Nuts:

    >>> from six.moves import filter, range
    >>> from itertools import islice
    >>> list(islice(filter(lambda x: x > 5, range(10)), 3))
    [6, 7, 8]

    >>> from nutsflow import Range, Filter, Take, Collect, _
    >>> Range(10) >> Filter(_ > 5) >> Take(3) >> Collect()
    [6, 7, 8]
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor. Nuts (and derived classes) can have arbitrary arguments.

        :param args args: Positional arguments.
        :param kwargs kwargs: Keyword arguments.
        """
        self.args = args
        self.kwargs = kwargs

    def __call__(self, iterable):
        """
        Nut (processor) can be called as a function and mapped on
        iterable elements within an iterable.

        :param iterable iterable: Iterable to process.
        :return: Iterable
        :rtype: iterable
        """
        return self.__rrshift__(iterable)

    def __rrshift__(self, iterable):
        """
        Chaining operator for Nuts. Needs to be overridden!

        Takes an input iterable and produces some output iterable.
        If the number of elements in the input and the output iterable
        does not change consider NutFunction instead.

        :param iterable iterable: Iterable to process.
        :return: Iterable
        :rtype: iterable
        :raise: NotImplementedError if not implemented.
        """
        raise NotImplementedError(
            'Needs to implement  __rrshift__ : ' + str(self.__class__.__name__))


class NutFunction(Nut):
    """
    Nut functions are are mapped onto each element of the input iterable.

    Example: Square is a Nut function

    >>> from nutsflow import Square, Collect, _
    >>> [1,2,3] >> Square() >> Collect()
    [1, 4, 9]
    """

    def __call__(self, element):
        """
        Override this method to transform the elements of an iterable.

        :param element: Element the function is applied to.
        :return: A transformed element
        :rtype: any
        :raise: NotImplementedError if not implemented.
        """
        raise NotImplementedError(
            'Needs to implement  __call__() : ' + str(self.__class__.__name__))

    def __rrshift__(self, iterable):
        """
        Map function onto iterable and return transformed iterable.
        Do not override!

        :param iterable: function is applied to the elements of the iterable.
        :return: transformed iterable.
        :rtype: iterable
        """
        return map(self, iterable)


class NutSource(Nut):
    """
    Sources are nuts that have no input iterable but produce an output
    iterable.
    """

    def __rrshift__(self, iterable):
        """
        Raises an exception when called. Sources have not input!
        Do not override! Override __iter__() instead.

        :param iterable iterable: Iterable
        :raise: SyntaxError if called.
        """
        raise SyntaxError(
            "Sources don't have inputs: " + str(self.__class__.__name__))

    def __iter__(self):
        """
        Return iterator over some data. Needs to be overridden!

        :return: Iterator for source data.
        :rtype: iterator
        :raise: NotImplementedError if not implemented.
        """
        raise NotImplementedError(
            'Needs to implement __iter__() :' + str(self.__class__.__name__))


class NutSink(Nut):
    """
    Sinks are nuts that do not guarantee to produce an iterable output.

    Sinks are typically at the end of a flow and typically aggregate the flow
    to a single output, e.g. the sum of its elements.
    Need to override __rrshift__()!
    """

    def __iter__(self):
        """
        Raises an exception when called. Sinks should not serve as sources.

        :raise: SyntaxError if called.
        """
        raise SyntaxError(
            'Sinks cannot be inputs: ' + str(self.__class__.__name__))

    def __call__(self, iterable):
        """
        Sinks can serve as functions applied to iterables within a flow.

        :param iterable: Sink takes iterable as input
        :return: Output of sink
        :rtype: any
        """
        return iter(iterable) >> self
