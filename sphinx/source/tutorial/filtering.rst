Filtering data
==============


Filter
------

A common task is to remove elements from a data flow. **nuts-flow**
provides ``Filter`` and ``FilterFalse`` for this purpose:

  >>> from nutsflow import *
  
  >>> Range(10) >> Filter(lambda x: x > 5) >> Collect()
  [6, 7, 8, 9]
  
  >>> Range(10) >> FilterFalse(lambda x: x > 5) >> Collect()
  [0, 1, 2, 3, 4, 5]

``Filter`` and ``FilterFalse`` take a predicate (Lambda) function that
must return a boolean value. If the predicate function is very simple
it can be written shorter using the :ref:`Underscore syntax`
  
  >>> from nutsflow import _
  
  >>> Range(10) >> Filter(_ > 5) >> Collect()
  [6, 7, 8, 9]
  
  >>> Range(10) >> FilterFalse(_ > 5) >> Collect()
  [0, 1, 2, 3, 4, 5]

  
Partition  
---------

If both 'sides' of a filter, the elements accepted **and** the elements 
rejected, are wanted the ``Partition`` nut can be used:

  >>> greater, smaller = Range(10) >> Partition(_ > 5)
  >>> greater >> Collect()
  [6, 7, 8, 9]
  >>> smaller >> Collect()
  [0, 1, 2, 3, 4, 5]
  
  >>> odd, even = Range(10) >> Partition(_ % 2)
  >>> odd >> Collect()
  [1, 3, 5, 7, 9]
  >>> even >> Collect()
  [0, 2, 4, 6, 8]
  
Note that ``Partition`` returns a tuple containing two iterators.


GroupBy
-------

Similar, but more powerful than ``Partition`` is ``GroupBy``, which allows
to group the elements of the flow according to a key function:

  >>> Range(10) >> GroupBy(_ > 5) >> Collect()
  [(False, [0, 1, 2, 3, 4, 5]), (True, [6, 7, 8, 9])]

``GroupBy`` returns an iterator over the groups, where each group is
a tuple with the result of the key function first and the elements of
the group second. If the result of the key function is not required
the *nokey* flag can be set to ``True``:

  >>> Range(10) >> GroupBy(_ > 5, nokey=True) >> Collect()
  [[0, 1, 2, 3, 4, 5], [6, 7, 8, 9]]
  
In contrast to ``Partition``, ``GroupBy`` is not limited to a boolean
key function. For instance, to group by the remainder of the division
by 3 simply call

  >>> Range(10) >> GroupBy(_ % 3) >> Collect()
  [(0, [0, 3, 6, 9]), (1, [1, 4, 7]), (2, [2, 5, 8])]

``GroupBy`` loads all data in memory and should be avoided for large data sets. 
If the data is sorted ``GroupBySorted`` can be used instead.


TakeWhile and SkipWhile
-----------------------

Occasionally, it is necessary to run a data flow until a certain
condition is met. ``TakeWhile(func)`` takes elements from the
iterable as long as the predicate function is true.
In the following example all number are collected until
the **first** negative number is encountered:

   >>> [2, 1, -1, 3, 4, -1] >> TakeWhile(_ > 0) >> Collect()
   [2, 1]
   
Similarily, ``SkipWhile(func)`` skips all elements while the predicate function
is true and returns the remainder of the iterable:

   >>> [2, 1, -1, 3, 4, -1] >> SkipWhile(_ > 0) >> Collect()
   [-1, 3, 4, -1]


