Reading and Sources
====================

TODO

.. code::

  with open(filepath) as lines:
    lines >> Filter(lamdba l: l.startswith('ERR')) >> Print() >> Consume()
