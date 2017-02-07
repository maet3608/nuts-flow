nuts-flow
=========

**nuts-flow** is largely a thin wrapper around *itertools* that allows
the chaining of iterators using the ``>>`` operator.
The aim is a more explict flow of data. The following examples show
a simple data processing pipeline using Python’s itertools versus **nuts-flow**:

  >>> from itertools import islice, ifilter
  >>> list(islice(ifilter(lambda x: x > 5, xrange(10)), 3))
  [6, 7, 8]


  >>> from nutsflow import Range, Filter, Take, Collect, _
  >>> Range(10) >> Filter(_ > 5) >> Take(3) >> Collect()
  [6, 7, 8]

Both examples extract the first three numbers within range [0, 9]
that are greater than five. However, the **nuts-flow** pipeline
is easier to understand than the nested *itertools* code.

Installation guide, API documentation and tutorials can be found
`here <https://maet3608.github.io/nuts-flow/>`_

