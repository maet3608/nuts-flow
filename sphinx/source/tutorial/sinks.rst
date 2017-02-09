Writing and Sinks
=================

TODO

.. code::

  with open(filepath) as f:
    f.writelines(Range(5) >> Square() >> Map(str))

