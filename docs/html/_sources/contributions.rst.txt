Contributions
=============

Contributions to **nuts-flow** are welcome. Please document the code following
the examples, provide unit tests and ensure that ``pytest`` runs without
errors. 


Environment
-----------

You will need git, Python, pytest, Sphinx installed.


Unit tests
----------

.. code ::

  $ cd nutsflow
  $ pytest
  ============================= test session starts =============================
  platform win32 -- Python 2.7.13, pytest-3.0.3, py-1.4.31, pluggy-0.4.0
  rootdir: C:\Maet\Projects\Python\nuts-flow, inifile: pytest.ini
  plugins: cov-2.3.1
  collected 138 items

  README.rst .
  nutsflow\base.py ..
  nutsflow\common.py ....
  nutsflow\function.py .........
  nutsflow\iterfunction.py ...........
  nutsflow\processor.py ...................
  nutsflow\sink.py ............
  nutsflow\source.py ......
  nutsflow\underscore.py .
  sphinx\source\installation.rst .
  sphinx\source\introduction.rst .
  sphinx\source\tutorial\custom_nuts.rst .
  sphinx\source\tutorial\debugging.rst .
  sphinx\source\tutorial\divide_conquer.rst .
  sphinx\source\tutorial\error_messages.rst .
  sphinx\source\tutorial\filtering.rst .
  sphinx\source\tutorial\nuts_basics.rst .
  sphinx\source\tutorial\performance.rst .
  sphinx\source\tutorial\practice_problems.rst .
  sphinx\source\tutorial\prerequisites.rst .
  sphinx\source\tutorial\rearranging.rst .
  sphinx\source\tutorial\recipes.rst .
  sphinx\source\tutorial\sinks.rst .
  sphinx\source\tutorial\sources.rst .
  sphinx\source\tutorial\transforming.rst .
  sphinx\source\tutorial\underscore.rst .
  tests\nutsflow\test_base.py ....
  tests\nutsflow\test_common.py ......
  tests\nutsflow\test_factory.py .........
  tests\nutsflow\test_function.py .........
  tests\nutsflow\test_iterfunction.py ...........
  tests\nutsflow\test_processor.py ...................................
  tests\nutsflow\test_sink.py ................
  tests\nutsflow\test_source.py .......
  tests\nutsflow\test_underscore.py ..
  tests\nutsflow\examples\test_examples.py .

  ========================= 182 passed in 19.58 seconds =========================



We are aiming at a code coverage of 100%. Run ``pytest --cov`` for verification.

.. code ::

  $ cd nutsflow
  $ pytest --cov

  ---------- coverage: platform win32, python 2.7.13-final-0 -----------
  Name                            Stmts   Miss  Cover
  ---------------------------------------------------
  nutsflow\base.py                   22      0   100%
  nutsflow\common.py                 27      0   100%
  nutsflow\examples\examples.py      57      0   100%
  nutsflow\factory.py                39      0   100%
  nutsflow\function.py               69      0   100%
  nutsflow\iterfunction.py           65      0   100%
  nutsflow\processor.py             160      0   100%
  nutsflow\sink.py                   85      0   100%
  nutsflow\source.py                 40      0   100%
  nutsflow\underscore.py             26      0   100%
  ---------------------------------------------------
  TOTAL                             590      0   100%



Documentation
-------------

Update Sphinx/HTML documentation as follows

.. code::

  cd sphinx
  make clean
  make html
  make test

  cd ..
  ./push_docs


Style guide
-----------

Code should be formatted following the `PEP-8 <https://www.python.org/dev/peps/pep-0008/>`_
style guide. 

Names of *nuts* shoulds be in CamelCase (just like class names) and describe an action,
e.g. ``ReadCSV`` but not ``CSVReader``.

Prefer *immutable* data types, e.g. tuples over lists, for outputs of nuts and
avoid nuts with *side-effects. Nuts should not *mutate* their input data but create
copies.

If a nut has no input it should be a *source*, for instance like ``Range``. 
If it doesn't output a generator or iterator it should be a *sink*, 
see ``Collect`` for example.
If a nut outputs the same number of elements it reads, it probably
is a *function* (e.g. ``Square``) otherwise a *processor*.