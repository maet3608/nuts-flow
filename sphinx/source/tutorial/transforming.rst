Data transformation
===================

Transformations are at the core of data flows and 
**nuts-flow** offers various *nuts* to this effect.

Map
---

The most common transformation is the mapping of
a function on the elements of a flow. ``Map(func)``
provides this functionality:

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

  
MapMulti
--------

Occasionally, it is necessary to apply different, independent 
mappings to the same data. One way is to process the data for each
mapping individually, e.g.
  
   >>> times2 = Range(5) >> Map(_ * 2) >> Collect()
   >>> greater3 = Range(5) >> Map(_ > 3) >> Collect()

However, if the generation or reading of the input data is
computationally expensive it is more efficient to use
``MapMulti``

  >>> times2, greater3 = Range(5) >> MapMulti(_ * 2, _ > 3)
  >>> times2 >> Collect()
  [0, 2, 4, 6, 8]
  >>> greater3 >> Collect()
  [False, False, False, False, True]

``MapMulti`` allows to perform an arbitray number of mappings
at the same time and returns iterators for each mapping.


MapCol
------

Often input data is organized in rows (records) and columns
and mappings for individual columns are wanted. 
``MapCol(columns, func)`` maps a function to the specified
columns of the input data:

  >>> negate = lambda x: -x
  >>> [(1, 2), (3, 4)] >> MapCol(0, negate) >> Collect()
  [[-1, 2], [-3, 4]]
  
  >>> [(1, 2), (3, 4)] >> MapCol(1, str) >> Collect()
  [[1, '2'], [3, '4']]
  
  >>> [(1, 2), (3, 4)] >> MapCol((0, 1), _ > 2) >> Collect()
  [[False, False], [True, True]]


TODO


  Get, GetCols
  Flatten, FlatMap, (Chunk => spit_combine?)
  Slice, Cycle ?

