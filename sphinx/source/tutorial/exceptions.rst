.. _exceptions:

Handling exceptions
====================

Data processing pipelines are typically composed of multiple nuts
and process a stream of data. If one of the nuts within the pipeline
fails the data stream breaks and processing stops.

Sometimes a more graceful handling of errors is needed and **nuts-flow**
provides the ``Try`` nut for this purpose.


Try
---

``Try(func, default)`` can wrap any nut function 
(but not other types of nuts such as processors) and handle exceptions 
raised by the wrapped nut.
In the following example a nut ``Div`` is defined, which computes 10/x
and is applied to a sequence of numbers: 

>>> from nutsflow import *
>>> Div = nut_function(lambda x : 10/x)
>>> [1, 5, 10] >> Div() >> Collect()
[10, 2, 1]

As it is this pipeline will break and not collect any results 
if any of the input elements is zero:

>>> [1, 0, 10] >> Div() >> Collect()
Traceback (most recent call last):
...
ZeroDivisionError: integer division or modulo by zero

Wrapping the ``Div`` function within a ``Try`` allows the pipeline
to ignore the input element that causes ``Div`` to fail. The problematic
element and the error message are printed to standard out 
but the pipeline does not break and collects all other elements:

>>> [1, 0, 10] >> Try(Div(), 'STDOUT') >> Collect()
ERROR: 0 : integer division or modulo by zero
[10, 1]

``Try`` allows defining a default value to be returned if the wrapped
function fails. In this case no error is printed the offending input element 
is replaced by the provided default value:

>>> [1, 0, 10] >> Try(Div(), -1) >> Collect()
[10, -1, 1] 

This kind of exception handling can be performed for nut functions 
or plain Python functions (user-defined or built-in). Here an example
where Python's logarithm function is wrapped and zero values are
ignored:

>>> from math import log
>>> [1, 0, 10] >> Try(log, default='STDOUT') >> Collect()
ERROR: 0 : math domain error 
[0.0, 2.302585092994046]

The ``default`` parameter can also be a function that takes the offending
input element ``x`` and the exception ``e`` as parameters. This allows
to replace offending inputs depending on the input value or the types of
exception raised.
In the following example negative input elements are replaced by
their absolute value and zero is replaced by ``None``.

>>> if_invalid = lambda x, e: -x if x < 0 else None
>>> [1, 0, -1, 10] >> Try(log, if_invalid) >> Collect()
[0.0, None, 1, 2.302585092994046]

As a last example, invalid inputs are replaced by the exception they
cause:

>>> if_invalid = lambda x, e: e
>>> [1, -1, 10] >> Try(log, if_invalid) >> Collect()
[0.0, ValueError('math domain error',), 2.302585092994046]

The default value for ``Try(x,default)`` is ``default='STDERR'``,
which ignores all elements that raise exceptions and prints error
message to stderr. For ``default='IGNORE'``, offending inputs are
ignored and no error messages are printed.



