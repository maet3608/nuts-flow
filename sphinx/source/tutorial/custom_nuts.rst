Custom nuts
===========

**nuts-flow** can easily be extended with custom nuts using wrappers, 
decorators or derived classes. To clarify the differences between the
approaches let us start with a simple filter. First, import **nutsflow**

>>> from nutsflow import *

then define a ``lambda`` function that returns ``True`` for elements
greater than five

>>> greater_than_5 = lambda x: x > 5

and finally filter numbers using ``Filter`` and the defined ``lambda`` 
predicate 

>>> Range(10) >> Filter(greater_than_5) >> Collect()
[6, 7, 8, 9]

By wrapping the lambda function via ``nut_filter`` a custom
filter nut can be created

>>> GreaterThan5 = nut_filter(lambda x: x > 5)

that operates the same way but can be directly used as a nut

>>> Range(10) >> GreaterThan5() >> Collect()
[6, 7, 8, 9]

Note the change from lowercase for ``greater_than_5`` to uppercase 
for ``GreaterThan5`` to signify the change from a Python function
to a **nuts-flow** nut. This is strongly recommended to avoid
confusion on how to use a function or nut. Nuts are generally
in uppercase and used with brackets while Python functions are lowercase
and used without brackets. 

For instance, both of the following examples are **invalid**. Here
``greater_than_5`` is confused as nut and called with additional brackets 

>>> Range(10) >> Filter(greater_than_5()) >> Collect()
Traceback (most recent call last):
...
TypeError: <lambda>() takes exactly 1 argument (0 given)

while ``GreaterThan5`` is used with missing brackets 

>>> Range(10) >> GreaterThan5 >> Collect()
Traceback (most recent call last):
...
TypeError: unsupported operand type(s) for >>: 'Range' and 'type'


`Wrappers` such as ``nut_filter(...)`` are suitable for simple one-line 
functions with a single parameter but become less readable when 
additional parameters are required,  e.g. filtering with a given threshold

.. code::

  GreaterThan = nut_filter(lambda x, threshold: x > threshold)
  Range(10) >> GreaterThan(5) >> Collect()

In this case `decorators` are a better solution

.. code::

  @nut_filter
  def GreaterThan(x, threshold):
      return x > threshold

  Range(10) >> GreaterThan(5) >> Collect()

Note that for wrappers and decorators there is a difference in the 
arguments depending on whether the nut is *defined* or *used*

**definitions:**

.. code::

  GreaterThan = nut_filter(lambda x, threshold: ...)

.. code::

  @nut_filter
  def GreaterThan(x, threshold): ...
  

**usage:**

.. code::

  x >> GreaterThan(threshold)

When *used* the first argument of the nut (here ``x``) appears as input 
on the  left side of the ``>>`` operator and the remaining parameters 
appear in brackets.

In rare (more advanced) cases custom nuts can be implemented
as classes derived from the relevant base classes (see ``base.py``).
Here an example implementation of the ``GreaterThan`` nut as a class

.. code::

  class GreaterThan(Nut):
      def __init__(self, threshold):
          self.threshold = threshold

      def __rrshift__(self, iterable):  # >> operator
          for x in iterable:
              if x > self.threshold:
                  yield x

Decorators and wrappers are shortcuts to create nut classes 
and the preferred method to implement custom nuts.      		      


Nut types
---------

**nuts-flow** provides six different types of wrappers/decorators

- :ref:`nut_source`
- :ref:`nut_sink`
- :ref:`nut_function`
- :ref:`nut_processor`
- :ref:`nut_filter`
- :ref:`nut_filterfalse`


nut_source
^^^^^^^^^^

Typical cases for custom *nut sources* are the reading of files
in specific formats or wrappers around databases. Here
two toy examples for a wrapper and a decorator around a nut
that generates ``n`` even numbers. First the wrapper approach

>>> EvenNumbers = nut_source(lambda n: (2*x for x in xrange(n)))

and here the decorator

.. code::

  @nut_source
  def EvenNumbers(n):
      return (2*x for x in xrange(n))

Both can be used as follows

>>> EvenNumbers(4) >> Collect()
[0, 2, 4, 6]


nut_sink
^^^^^^^^

Sinks receive an iterable and can return any result (not necessarily
an iterable). The following example re-implements the ``Join`` sink
that already exists in **nuts-flow** using a wrapper

>>> Join = nut_sink(lambda it, sep: sep.join(map(str, it)))

>>> Range(5) >> Join(':')
'0:1:2:3:4'

or using the decorator method

.. code::

  @nut_sink
  def Join(iterable, sep):
      return sep.join(map(str, iterable))

Note that while ``Join`` is a sink it returns an iterable (here a string)
and can therefore serve as input to other nuts

>>> Range(5) >> Join(':') >> Count()
9

The general rule is, if a nut collects/aggregates data in memory or
does not return an iterable result is should be implemented as a *sink*
(despite being able to be input to other nuts). On the other hand,
if a nut processes data *on-the-fly* and returns an iterator it should
**not** be a *sink*.


nut_function
^^^^^^^^^^^^

A *nut function* is a nut that is applied to each element in the data
flow and returns a result for each element. Consequently, when a nut
function is applied to a data flow the values of the elements change but
not their number. The following example function multiplies each element of
the data flow by ``n``

>>> Times = nut_function(lambda x, n: x * n)

and here the same function via a decorator

.. code::

  @nut_function
  def Times(x, n):
      return x * n

Usage is identical for both the wrapper and the decorator

>>> Range(5) >> Times(2) >> Collect()
[0, 2, 4, 6, 8]


nut_processor
^^^^^^^^^^^^^

A *nut processor* takes an iterable and returns an iterable but the  
number of elements in the output iterable can differ - this is different
to a :ref:`nut_function`.  If the numbers don't change both methods
can be used but a :ref:`nut_function` will be simpler. For instance,
here the ``Times`` nut re-implemented as a processor:

>>> Times = nut_processor(lambda iterable, n: (x * n for x in iterable))

Processors are needed if the number of elements in the flow changes, e.g.
here a processor nut that duplicates each element of the flow 

.. code::

  @nut_processor
  def Duplicate(iterable):
      for e in iterable:
          yield e
          yield e
  
  Range(5) >> Duplicate() >> Collect()
  [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]

or more generic, a processor that clones each element ``n`` times

.. code::

  @nut_processor
  def Clone(iterable, n):
      for e in iterable:
          for _ in xrange(n):
              yield e
  
  Range(5) >> Clone(2) >> Collect()
  [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]

Processors can be used to filter elements from a data flow but
typically the *filter nuts* described next are more appropriate
and easier to implement.


nut_filter
^^^^^^^^^^

As described above, *nut filters* extract elements from a data flow.
Here a nut that extracts all numbers that are in a given interval

>>> InInterval = nut_filter(lambda x, a, b: a <= x <= b)

and the same filter implemented using the decorator

.. code::

  @nut_filter
  def InInterval(x, a, b):
      return a <= x <= b

and how it is used

>>> Range(10) >> InInterval(3, 6) >> Collect()
[3, 4, 5, 6]


nut_filterfalse
^^^^^^^^^^^^^^^

Occasionally it is easier to implement a filter that extracts
element that are **not** meeting a given condition. The 
``nut_filterfalse`` wrapper/decorator is available for this 
use case. For instance, the following nut filters out all
elements that are **not** equal to given value

>>> Not = nut_filterfalse(lambda x, val: x == val)

or implemented via the decorator

.. code::

  @nut_filterfalse
  def Not(x, val):
      return x == val

and a usage example

>>> [1, 2, 3, 4] >> Not(2) >> Collect()
[1, 3, 4]

``nut_filterfalse`` is largely used to wrap existing predicate
functions as nuts. For example, given a function ``isnull(x)``
we can simply write  

.. code::

	IsValid = nut_filterfalse(isnull)  

which is shorter and more readable than

.. code::

	IsValid = nut_filter(lambda x: not isnull(x))  
