Common error messages
=====================

``'Wrapper' object is not callable``
------------------------------------------------------------------

Additional brackets when calling nut:

>>> from nutsflow import *
>>> greater0 = Filter(lambda x : x > 0)
>>> [2, -1, 3] >> greater0() >> Collect()  # doctest: +SKIP
...
TypeError: 'Wrapper' object is not callable
  
Should be: 

>>> greater0 = Filter(lambda x : x > 0)
>>> [2, -1, 3] >> greater0 >> Collect()
[2, 3]

  
  
``unsupported operand type(s) for >>``
------------------------------------------------------------------

Missing brackets when calling nut:

>>> Greater0 = nut_filter(lambda x: x > 0)  
>>> [2, -1, 3] >> Greater0 >> Collect()  # doctest: +SKIP
...
TypeError: unsupported operand type(s) for >>: 'list' and 'type'
  
Should be:   

>>> Greater0 = nut_filter(lambda x: x > 0)  
>>> [2, -1, 3] >> Greater0() >> Collect()
[2, 3]


  

``name '_' is not defined``
------------------------------------------------------------------

Typically encountered when using ``_`` without importing it.
Example:

>>> from nutsflow import *
>>> [2, -1, 3] >> Filter(_ > 0) >> Collect()  # doctest: +SKIP
...
NameError: name '_' is not defined
  
Since ``_`` is a common name for place-holder variables the
explicit import of ``_`` is required:

>>> from nutsflow import *
>>> from nutsflow import _
>>> [2, -1, 3] >> Filter(_ > 0) >> Collect()
[2, 3]
