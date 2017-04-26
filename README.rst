
.. image:: pics/nutsflow_logo.gif
   :align: center

- `Introduction <https://maet3608.github.io/nuts-flow/introduction.html>`_
- `Installation <https://maet3608.github.io/nuts-flow/installation.html>`_
- `Tutorial <https://maet3608.github.io/nuts-flow/tutorial/introduction.html>`_
- `Documentation <https://maet3608.github.io/nuts-flow/>`_
- `Code <https://github.com/maet3608/nuts-flow>`_

**nuts-flow** is largely a thin wrapper around Python’s *itertools* that allows
the chaining of iterators using the ``>>`` operator. This lead to more
readable code that shows the flow of data. The following examples show
a simple data processing pipeline comparing *itertools* with **nuts-flow**:

  >>> from itertools import islice, ifilter
  >>> list(islice(ifilter(lambda x: x > 5, xrange(10)), 3))
  [6, 7, 8]


  >>> from nutsflow import Range, Filter, Take, Collect, _
  >>> Range(10) >> Filter(_ > 5) >> Take(3) >> Collect()
  [6, 7, 8]

Both examples extract the first three numbers within range [0, 9]
that are greater than five. However, the **nuts-flow** pipeline
is easier to understand than the nested *itertools* code.

**nuts-flow** is the base for `nuts-ml <https://github.com/maet3608/nuts-ml>`_, 
which is described `here <https://maet3608.github.io/nuts-ml/>`_ .
