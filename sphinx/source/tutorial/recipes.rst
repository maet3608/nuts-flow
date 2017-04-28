.. _recipes:

Recipes
=======

A collection of common problems with solutions. Make sure **nutsflow** has been imported.


Write CSV file with column names
--------------------------------

.. code:: Python

  with WriteCSV(filepath) as writer:
      [('Col1', 'Col2')] >> writer
      [(1, 2), (3, 4)] >> writer
      

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
loading the CSV file, dropping the header line, converting Arabic numbers
(that are loaded as strings) to integers and collecting the results in 
a dictionary

>>> from nutsflow import ReadCSV, Drop, MapCol, GetCols, Collect  
>>> fpath = 'tests/data/arab2num.csv'
>>> arab2roman = ReadCSV(fpath) >> Drop(1) >> MapCol(0, int) >> Collect(dict)
>>> arab2roman[2]
'II'


For the reversed mapping (Roman to Arabic), we just flip the columns via ``GetCols``
and use ``skipheader=1`` to skip the header line

>>> roman2arab = (ReadCSV(fpath, skipheader=1) >> MapCol(0, int) >> 
... GetCols(1, 0) >> Collect(dict))
>>> roman2arab['III']
3
