.. _transforming:

Data transformation
===================


The (element-wise) transformation of data is, together with
:ref:`filtering <filtering>`, at the very core of data flows and
**nuts-flow** provides various nuts for this purpose.


Elementwise transformations
---------------------------

The most common transformation is the mapping of a function on a flow.

Map
^^^

``Map(func)`` nut takes a function and applies it to each element of
the input iterable. See the following examples: and 

>>> from nutsflow import *
>>> from nutsflow import _
  
>>> Range(5) >> Map(lambda x : x * x) >> Collect()
[0, 1, 4, 9, 16]

>>> Range(5) >> Map(_ * 2) >> Collect()
[0, 2, 4, 6, 8]

>>> Range(5) >> Map(_ > 2) >> Collect()
[False, False, False, True, True]

>>> Range(5) >> Map(str) >> Collect()
['0', '1', '2', '3', '4']

Note that ``Map`` can transform elements of the flow in arbitrary ways
but cannot change the number of elements in the flow.

  
MapMulti
^^^^^^^^

Occasionally, it is necessary to apply different, independent 
mappings to the same data. One way is to process the data for each
mapping individually, e.g.
  
>>> times2 = Range(5) >> Map(_ * 2) >> Collect()
>>> greater3 = Range(5) >> Map(_ > 3) >> Collect()

However, if the generation or reading of the input data is
computationally expensive it is more efficient to use ``MapMulti``
and avoid rereading the input multiple times.

>>> times2, greater3 = Range(5) >> MapMulti(_ * 2, _ > 3)
>>> times2 >> Collect()
[0, 2, 4, 6, 8]
>>> greater3 >> Collect()
[False, False, False, False, True]

Note that ``MapMulti`` performs an arbitray number of mappings
at the same time and returns iterators for each mapping.



Tabular data
------------

Often input data is organized in rows (records) and columns,
and transformations for selected columns only are needed.

MapCol
^^^^^^

``MapCol(columns, func)`` maps a function to the specified
columns of the input data and leaves other columns unchanged.

Given the following table with tuples as records

>>> table = [ (1, 2), 
...           (3, 4) ]

the example flow below negates all numbers in column 0:
  
>>> negate = lambda x: -x
>>> table >> MapCol(0, negate) >> Print() >> Consume()
(-1, 2)
(-3, 4)
  
or let us convert each number in the second column to a string:  
  
>>> table >> MapCol(1, str) >> Collect()
[(1, '2'), (3, '4')]
  
``MapCol`` can apply the same mapping to multiple columns at
the same time. For instance, checking if numbers in columns
0 and 1 are greater than two: 
  
>>> table >> MapCol((0, 1), _ > 2) >> Collect()
[(False, False), (True, True)]
  
Note that input data must be an iterable of tuples or other 
indexable objects and the flow iterates over these records.
To iterate over all elements of a table individually use
:ref:`Flatten`.  


Get
^^^

``Get(start, end, step)`` operates similar to Python's slicing 
``[start:end:step]`` and extracts individual elements or
slices from table records. For instance, given the following table

>>> table = [ (1, 2, 3), 
...           (4, 5, 6) ]

``Get(1)`` extracts all elements in column 1 of the table:  

>>> table >> Get(1) >> Collect()
[2, 5]
  
Note that, since a single column was extracted, the output is a 
list of numbers and not a list of tuples anymore.

``Get(0, 2)`` extracts column 0 to 1: 
    
>>> table >> Get(0, 2) >> Print() >> Consume()
(1, 2)
(4, 5)
  
and ``Get(0, 3, 2)`` extracts column 0 to 2 with stride 2:   

>>> table >> Get(0, 3, 2) >> Collect()
[(1, 3), (4, 6)]
  
Note that in agreement with Python's slicing the index of the
``end`` column is *exclusive*.



GetCols
^^^^^^^

The ``Get`` nut described above can extract only consecutive
table columns in order. `` GetCols(*columns)`` allows to extract
arbitray columns in arbitrary order. Given the following table

>>> table = [ (1, 2, 3), 
...           (4, 5, 6) ]

``GetCols(1)`` extracts column 1 of the table:

>>> table >> GetCols(1) >> Collect()
[(2,), (5,)]
  
Note that in contrast to ``Get(1)`` a list of (single element)
tuples is returned.

The following example extracts columns 2, 1, and 0, and
effectively reverses the column order of the table: 

>>> table >> GetCols(2, 1, 0) >> Print() >> Consume()
(3, 2, 1)
(6, 5, 4)
  
``GetCols`` can even duplicate columns, e.g. duplicating 
column 1 and removing column 0 can be achieved as follows:

>>> table >> GetCols(1, 1, 2) >> Print() >> Consume()
(2, 2, 3)
(5, 5, 6)



Flatten data
------------

Hierarchical data structures such as lists of lists frequently
need to be converted to flat structures. ``Flatten`` and ``FlatMap``
are two nuts for flatting data.

Flatten
^^^^^^^

``Flatten`` flattens all iterables within the input and returns
an iterator over the result. For instance:

>>> [(1, 2), (3, 4, 5), 6] >> Flatten() >> Collect()
[1, 2, 3, 4, 5, 6]

Note that only one level is flattend. Deeper structures remain
unchanged

>>> [(1, 2), ((3, 4), 5), 6] >> Flatten() >> Collect()
[1, 2, (3, 4), 5, 6]
  
but can be, of course, flattend by sucessive calls of ``Flatten``:

>>> [(1, 2), ((3, 4), 5), 6] >> Flatten() >> Flatten() >> Collect()
[1, 2, 3, 4, 5, 6]


FlatMap
^^^^^^^

A common operation is a ``Map`` followed by a ``Flatten`` and ``FlatMap``
is a nut that provides this operation in one call. See the following 
examples to dublicate all numbers in a list of numbers:

>>> dup = lambda x: (x, x)

>>> [0, 1, 2] >> Map(dup) >> Collect()
[(0, 0), (1, 1), (2, 2)]

>>> [0, 1, 2] >> Map(dup) >> Flatten() >> Collect()
[0, 0, 1, 1, 2, 2]

>>> [0, 1, 2] >> FlatMap(dup) >> Collect()
[0, 0, 1, 1, 2, 2]

