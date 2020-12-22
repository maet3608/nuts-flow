Performance
===========

**nuts-flow** does not support concurrency in general but provides
nuts that can improve performance by caching or parallelization.


MapPar
------

Applying a function concurrently to the elements of a flow can be achieved
with the ``MapPar`` nut. The following toy example converts numbers to their
*absolute values* by applying the ``abs`` function in parallel

>>> from nutsflow import *

>>> [-1, -2, -3] >> MapPar(abs) >> Collect()
[1, 2, 3]

Note that the order of the elements in the iterable is preserved.
Currently, ``MapPar`` is of limited use, since 1) the function applied 
must be `pickable <https://docs.python.org/2/library/pickle.html>`_
and 2) ``MapPar`` creates parallel processes, which are computationally 
expensive to start. 


Cache
-----

**nuts-flow** supports the *caching* of results to disk. Here an 
example in pseudo code

.. code:: python

  with Cache() as cache:
      for i in range:
          data >> expensive_op >> cache >> ... >> Collect()

Note that *caching* is only useful if 1) the elements to cache are
time-consuming to compute, 2) can be loaded faster than recreated,
and 3) the same data flow is executed multiple times,
where in the first run the cache is filled and then is used in all
subsequent runs.

A common use case is *machine learning for vision*, where images
are preprocessed and a classifier is trained by repeatedly executing 
a data flow:

.. code:: python

  with Cache() as cache:
      for epoch in xrange(100):
          images >> preprocess >> cache >> network.train() >> Consume()

Cached elements are pickled to a temporary folder which is deleted
when the ``with`` block is exited. The cache can be cleared as follows:

.. code:: python

  with Cache() as cache:
      ...
      cache.clear()


Prefetch
--------

*Prefetching* is another common method employed in (GPU-based) machine learning
to speed up a data flow. Here data is pre-fetched (and pre-processed) 
on a separate CPU thread while the GPU is performing machine learning 
on another chunk of data:

.. code:: python
   
   images >> preprocess >> Prefetch() >> network.train() >> Consume()


The following two examples demonstrate the difference between processing
a data flow with and without pre-fetching. First a flow *without pre-fetching*
that takes one number and prints it

.. code:: python

  >>> Range(5) >> Print() >> Take(1) >> Consume()
  0

now the same flow but *with pre-fetching*

.. code:: python

  >>> Range(5) >> Print() >> Prefetch() >> Take(1) >> Consume()
  0
  1



