============
Installation
============

Pip or clone
------------

Installation via ``pip`` from `PyPi <https://pypi.python.org/pypi>`_ :

.. code::
  
  pip install nutsflow
  

or ``git clone`` from `GitHub <https://github.com/>`_  
for bleeding-edge version: 
  
.. code::

  git clone https://github.com/maet3608/nuts-flow.git
  cd nuts-flow
  python setup.py install
  pytest

  
Verification
------------
  
Verify that it works:

.. doctest::

  python
  >>> from nutsflow import *
  >>> Range(5) >> Square() >> Collect()
  [0, 1, 4, 9, 16]
  
  
Print version number:

.. doctest::

  python
  >>> import nutsflow
  >>> nutsflow.__version__
  '1.0.6'
  
  
  
Virtual environment
-------------------

Create virtual environment:

.. code::

  pip install virtualenv
  cd my_projects
  virtualenv vnuts

  
Activate/deactivate  environment:

Linux, Mac:

.. code::

  $ source vnuts/bin/activate
  $ deactivate

  
Windows:

.. code::

  > vnuts\Scripts\activate.bat
  > vnuts\Scripts\deactivate.bat
  
  
Install **nuts-flow**:

.. code::
  
  source vnuts/bin/activate
  pip install nuts-flow


