.. _underscore:

Recipes
=======

A collection of common problems with solutions. Make sure **nutsflow** has been imported.

  >>> from nutsflow import *


Load a mapping file
-------------------

From a file with two columns create a directory that maps
values in one column to the other. For instance, the following
file contains Arabic numbers and their Roman counterparts.

.. code::

  arab,roman
  1,I
  2,II
  3,III

We create a Python dictionary that maps Arabic to Roman numbers by
loading the CSV file, skipping the header line, converting Arabic numbers
(that are loaded as strings) to integers and collecting the results in 
a dictionary

  >>> fpath = 'tests/data/arab2num.csv'

  >>> arab2roman = ReadCSV(fpath, skipheader=1) >> MapCol(0, int) >> Collect(dict)
  >>> arab2roman[2]
  'II'


For the reversed mapping (Roman to Arabic), we just flip the columns via ``GetCols``

  >>> roman2arab = (ReadCSV(fpath, skipheader=1) >> MapCol(0, int) >> 
  ... GetCols(1, 0) >> Collect(dict))
  >>> roman2arab['III']
  3




