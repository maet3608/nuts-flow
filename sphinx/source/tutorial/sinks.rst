.. _sinks:

Writing to Sinks
================

Sinks are typically at the end of a data flow and needed to *drive* 
the flow. Without a sink the flow is not processing any data.


Python functions
----------------

All Python functions that accept iterators or iterables can
serve as sinks, e.g. ``list``, ``set``, ``dict``, ``sum``,
``file.writelines``, ...,  but since they are not nuts
they do not support the ``>>`` operator and need to be 
called as functions. Here some examples

.. doctest::

  >>> from nutsflow import *
  >>> from nutsflow import _

  >>> list(Range(10) >> Filter(_ < 4) >> Square())
  [0, 1, 4, 9]

  >>> set([1, 2, 1, 3] >> Square())
  set([1, 4, 9])

  >>> dict([('one', 1), ('four', 2)] >> MapCol(1, Square()))
  {'four': 4, 'one': 1}


.. code::

  with open(filepath) as f:
      f.writelines(Range(4) >> Square() >> Format('{}'))

    
Nuts
----

Collect
^^^^^^^

The most commonly used sink is ``Collect``, 
which collects all elements of the input iterable in a list.

>>> Range(10) >> Filter(_ < 4) >> Collect()
[0, 1, 2, 3]
  
``Collect(container)`` also allows to specify a container to collect 
the data in. Any Python function that accept iterators or iterables 
is a valid container, e.g.

>>> [1, 2, 1, 3] >> Square() >> Collect(set)
set([1, 4, 9])

>>> [('one', 1), ('four', 2)] >> MapCol(1, Square()) >> Collect(dict)
{'four': 4, 'one': 1}

>>> Range(10) >> Square() >> Collect(sum)
285

>>> Range(5) >> Map(str) >> Collect(':'.join)
'0:1:2:3:4'

``Collect`` stores all data in memory and is not suitable 
for large data sets. In such a case use :ref:`WriteCSV`
to write data to the file system.


Head and Tail
^^^^^^^^^^^^^

:ref:`Collect` collects **all** elements of the input. Often only
the first or last *n* elements are needed. ``Head(n)`` collects
the first *n* elements and ``Tail(n)`` the last *n* elements

>>> Range(10) >> Head(4)
[0, 1, 2, 3]

>>> Range(10) >> Tail(4)
[6, 7, 8, 9]

Similar to :ref:`Collect`,  ``Head``  and ``Tail`` allow to
specify a container to store the result in

>>> [1, 2, 1, 3, 2] >> Head(3, set)
set([1, 2])

>>> Range(10) >> Tail(3, sum)
24



Common nuts
^^^^^^^^^^^

**nuts-flow** provides nuts for common aggregator functions
such as ``Sum``, ``Min``, ``Max``, ``ArgMax``, ``ArgMin``,
and ``Join``. For instance, instead of writing 

>>> Range(10) >> Collect(sum)
45

one can simply write  

>>> Range(10) >> Sum()
45

``Join`` is the nuts equivalent of Python's ``join`` method
but automatically converts numbers to strings

>>> Range(5) >> Join(':')
'0:1:2:3:4'

``Min`` and ``Max`` return the minimum or the maximum element
of a data flow and allow to specify a key function and a 
default value in case of an empty data stream. For instance,
find the longest string

>>> ['1', '123', '12'] >> Max(key=len)
'123'

and return the empty string if there is no data  

>>> [] >> Max(len, default='')
''

``ArgMin`` and ``ArgMax`` return the **index** of the smallest or
largest element and possibly the element itself. For example,
the index of the longest string

>>> ['12', '1', '123'] >> ArgMax(key=len)
2

or the index and the string itself  

>>> ['12', '1', '123'] >> ArgMax(len, retvalue=True)
(2, '123')

A default value is also supported to deal with empty input data

>>> [] >> ArgMax(default=(0, None), retvalue=True)
(0, None)

>>> [] >> ArgMax(default='empty')
'empty'


Count and CountValues
^^^^^^^^^^^^^^^^^^^^^

To count the number of elements in a flow or the numbers of
different elements in a flow ``Count`` and ``CountValues``
are provided.

``Count`` simply consumes the data flow and counts the number
of elements

>>> [1, 2, 1, 3, 2] >> Count()
5

>>> 'abaacc' >> Count()
6

while ``CountValues`` counts the frequencies of the different values 
and returns a dictionary

>>> 'abaacc' >> CountValues()
{'a': 3, 'c': 2, 'b': 1}

``CountValues`` can also return the *relative frequencies* instead
of the *absolute counts*  

>>> 'aabaab' >> CountValues(True)
{'a': 1.0, 'b': 0.5}



Reduce
^^^^^^

``Reduce(func [,initiaizer])`` reduces a flow of data elements to a 
single element, using a given function. ``Reduce`` is a thin wrapper around 
Python's `reduce <https://docs.python.org/2/library/functions.html#reduce>`_
function.

The following example computes the product of a list of numbers

>>> [1, 2, 3] >> Reduce(lambda a, b: a * b)
6

``Reduce`` can be called with an initalizer, which specifies the first
element used in the reduction

>>> ['one', 'two'] >> Reduce(lambda a, b: a + b, 'start')
'startonetwo'


Consume
^^^^^^^

If a data flow has side effects (e.g. printing, writing to a file) 
but no interesting result itself the ``Consume`` nut can be used.
It drives a data flow but does not collect or discards any
of its results. For instance, the following flow has the
side effect of printing numbers:

>>> Range(3) >> Print() >> Consume()
0
1
2

In contrast, the following flow processes data but returns nothing

>>> Range(3) >> Square() >> Consume()

while the next flow has no sink and therefore only returns an iterator
object but does not process any data

>>> Range(3) >> Square() >> Print()
<itertools.imap object at ...>

The former because there is no side effect and the later
because there is no sink that drives the flow.


WriteCSV
^^^^^^^^

``WriteCSV(filepath, cols, skipheader, fmtfunc, **kwargs)`` writes
data in *Comma Separated Values format* (CSV) to the specified file. 
For instance,

.. code::

   [(1, 2), (3, 4)] >> WriteCSV('data.csv')

would create the file ``data.csv`` with the following content
   
:: 

  1,2
  3,4
  
  
However, to ensure that files are closed safely it is preferable to
use ``WriteCSV`` in conjunction with the ``with`` statement

.. code::

  with WriteCSV('data.csv') as writer:
     [(1, 2), (3, 4)] >> writer

It is possible to select the columns to write and to skip a given
number of header lines if needed. For example,

.. code::

  with WriteCSV('data.csv', cols=(1,0), skipheader=1) as writer:
     [('a', 'b', 'c'), (1, 2, 3), (4, 5, 6)] >> writer
     
will write the following data to  ``data.csv``: 
     
::

  2,1
  5,4    

while  

.. code::

  with WriteCSV('data.csv') as writer:
     [('a', 'b', 'c'), (1, 2, 3), (4, 5, 6)] >> writer

will write  
     
::

  a,b,c
  1,2,3
  4,5,6      

In addition to CSV other formats such as *Tab Separated Values* (TSV)
can be written by providing the appropriate delimiter
  
.. code::

  with WriteCSV('data.csv', delimiter='\t') as writer:
     [(1,2), (3,4)] >> writer

and values can be formatted using ``fmtfunc``. For example,

.. code::

  with WriteCSV('data.csv', fmtfunc=lambda x: 'num:'+str(x)) as writer:
     [(1, 2, 3), (4, 5, 6)] >> writer

will output     

::

  num:1,num:2,num:3
  num:4,num:5,num:6

          
Note that data does not need to be organized in tuples. Simple
data streams can be written as well:      
     
.. code::

  with WriteCSV('data.csv') as writer:
      Range(10) >> writer

     
``WriteCSV`` is a thin wrapper around Pythons ``csv.writer`` and
the ``kwargs`` of ``WriteCSV`` are passed on to ``csv.writer``.
See https://docs.python.org/2/library/csv.html for more details.
