============
Installation
============

Standard
--------

Installation via ``pip`` from `PyPi <https://pypi.python.org/pypi>`_ 

.. code::
  
  pip install nutsflow
  

Verification
------------
  
Quick check that it works

.. doctest::

  python
  >>> from nutsflow import *
  >>> Range(5) >> Square() >> Collect()
  [0, 1, 4, 9, 16]
    
    
You can also run the entire unit test suite using ``pytest``:

.. code::
  
  cd my_python_path/site-packages/nutflow
  pytest


.. note::

  If you don't know where your ``site-packages`` are, run the following code

  .. code::

    python -c "import site; print(site.getsitepackages())"
    ['C:\\Maet\\Software\\Anaconda', 'C:\\Maet\\Software\\Anaconda\\lib\\site-packages']      


Bleeding-edge
-------------

If you want the bleeding-edge version, install via
``git clone`` from `GitHub <https://github.com/>`_ 
  
.. code::

  git clone https://github.com/maet3608/nuts-flow.git
  cd nuts-flow
  python setup.py install
  pytest


Upgrade
-------  

For upgrading an existing installation

.. code::
  
  pip install nutsflow --upgrade

or if installed via ``git clone`` and ``setup.py``

.. code::
  
  cd nuts-flow
  python setup.py install --force    
  
  
Virtual environment
-------------------

Create virtual environment:

.. code::

  pip install virtualenv
  cd my_projects
  virtualenv vnuts

  
Activate/deactivate  environment:

**Linux, Mac**

.. code::

  $ source vnuts/bin/activate
  $ deactivate

  
**Windows**

.. code::

  > vnuts\Scripts\activate.bat
  > vnuts\Scripts\deactivate.bat
  
  
Install **nuts-flow** in virtual environment (here for Linux, Mac)

.. code::
  
  source vnuts/bin/activate
  pip install nutsflow


