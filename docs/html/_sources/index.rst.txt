.. Nutsflow documentation master file

Welcome to nuts-flow
====================

.. image:: pics/nutsflow_logo.gif
   :align: center

**nuts-flow** is a flow-programming framework based on the chaining of 
iterators using the ``>>`` operator. Here a small example

>>> from nutsflow import Range, Filter, Take, Collect, _
>>> Range(10) >> Filter(_ > 5) >> Take(3) >> Collect()
[6, 7, 8]

For a quick start have a look at the :ref:`Introduction` and for
more detailed information see the :ref:`Tutorial` .


.. toctree::
   :maxdepth: 1

   introduction
   installation   
   tutorial/introduction
   contributions
   nutsflow


Indices
=======

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

