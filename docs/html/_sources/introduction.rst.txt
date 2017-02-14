Introduction
============

**nuts-flow** is a data processing pipeline that is largely based on Python's 
`itertools <https://docs.python.org/2/library/itertools.html>`_.

**nuts** are thin wrappers around itertool functions and
provide a ``>>`` operator to chain iterators in pipelines
to construct data flows. The result is a more explict flow of data.

The following two examples show the same data flow. The first 
using Python's itertools and the second using **nuts-flow**:

>>> from itertools import islice, ifilter
>>> list(islice(ifilter(lambda x: x > 5, xrange(8)), 3))
[6, 7]

>>> from nutsflow import Range, Filter, Take, Collect, _
>>> Range(8) >> Filter(_ > 5) >> Take(3) >> Collect()
[6, 7]

Both data flows extract the first three integers 
in the interval [0, 8[ that are greater than five. However, 
the linear arrangment of processing steps with **nuts-flow** is
easier to read than the nested calls of itertool functions.

**nuts-flow** is the base library for 
`nuts-ml <https://github.com/maet3608/nuts-ml>`_, a
data pre-processing pipeline for (GPU-based) machine learning.