Prerequisites
=============

**nuts-flow** is based on *iterators* and makes frequent use of *lambda* functions.
If you are already familiar with these concepts go ahead and skip this section.


Lambda functions
----------------

Commonly functions are defined via the ``def`` keyword and a function name,
e.g.:

.. code:: pythonun

  def add(a, b):
      return a + b

*Lambda* functions or so called *anonymous* functions are an alternative method
to define very short functions (without a name) that are typically used only once.
For instance, the ``add`` function above can be written as follows

.. code:: python

  lambda a, b: a + b
  
Since functions are first class citizens in Python they can be assigned 
to variables and called by name as well

>>> add = lambda a, b: a + b
>>> add(1, 2)
3

The most common use case, however, is as a anonymous function for other 
functions such as ``sorted``, ``max`` or ``filter``.  For example, 
to extract numbers greater than 2 from a list we could write

>>> numbers = [1, 2, 3, 4]
>>> filter(lambda x: x > 2, numbers)
[3, 4]

**nuts-flow** has a special notation for even shorter function definitions, 
following the *underscore notation* from `Scala <https://www.scala-lang.org/>`_.
Using the underscore, the above filtering can be expressed 
even more succinctly as

>>> from nutsflow import _
>>> filter(_ > 2, numbers)
[3, 4]
   
The underscore essentially serves as a place holder for the numbers of the list.   
Note that the underscore notation in **nuts-flow** is very limited and only
simple expression (e.g. ``_ + 1``, ``_ <= 3``, ...) are supported. More details
can be found in Section :ref:`Underscore syntax` .


Iterators
---------

Iterators are needed to process data that doesn't fit in memory, e.g. lines of a 
very large file, permutations of a string, ..., or even infinitely large data such 
as counters or random numbers.

A Python `Iterator <https://wiki.python.org/moin/Iterator>`_ is any object that 
provides a ``next`` method, which returns elements when called and raises a 
``StopIteration`` exception when depleted. Here an iterator that returns 
even numbers up to a given maximum

>>> class Even():
...     def __init__(self, maximum):
...         self.counter = 0
...         self.maximum = maximum
...
...     def __iter__(self):
...         return self
...
...     def next(self):
...         self.counter += 2
...         if self.counter > self.maximum:
...             raise StopIteration
...         return self.counter
...
          
The ``__iter__`` method make the iterator *iterable* and enables 
its usage in ``for`` loops, list comprehensions or functions 
that take iterables

>>> even = Even(6)
>>> for e in even:
...     print e
2
4
6

There are three important properties of iterators to keep in mind. 
Firstly, an iterator is lazy. It doesn't produce anything until asked. 
There needs to be a consumer.
For instance, ``even = Even(100000)`` creates the iterator but does not 
create any numbers.

Secondly, an iterator has state and subsequent calls will advance its state.
Thirdly, once an iterator is depleted it needs to be recreated to be used 
again

>>> even = Even(10)

>>> [e for e in even]
[2, 4, 6, 8, 10]

>>> [e for e in even]
[]

>>> even = Even(10)
>>> [e for e in even]
[2, 4, 6, 8, 10]


Iterators can be chained to build complex data processing pipelines
that consume very little memory. Python's 
`itertools <https://docs.python.org/2/library/itertools.html>`_ 
library provides many functions for this purpose. The following toy
example uses itertools to extract the first three integers greater 
than five in the interval [0..8[

>>> from itertools import islice, ifilter
>>> list(islice(ifilter(lambda x: x > 5, xrange(8)), 3))  
[6, 7]


**nuts-flow** is largely based on Python’s itertools but aims to 
make the data flow more explict and readable by introducing
the  ``>>`` operator for chaining

>>> from nutsflow import Range, Filter, Take, Collect, _ 
>>> Range(8) >> Filter(_ > 5) >> Take(3) >> Collect()
[6, 7]

