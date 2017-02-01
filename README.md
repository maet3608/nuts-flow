# Nuts-flow

A simple dataflow framework in Python

API documentation and tutorials can be found here:  
https://pages.github.ibm.com/aur/nuts-flow/


Nuts-flow is a thin wrapper around Python’s itertools that allows
the chaining of operations on iterables using the ‘>>’ operator.
The aim is a more explict flow of data. The following examples show
a simple data flow using Python’s itertools versus Nuts-flow:

```
>>> from itertools import islice, ifilter  
>>> list(islice(ifilter(lambda x: x > 5, xrange(10)), 3))  
[6, 7, 8]
```

```
>>> from nutsflow import Range, Filter, Take, Collect, _  
>>> Range(10) >> Filter(_ > 5) >> Take(3) >> Collect()  
[6, 7, 8]  
```

Both examples are equivalent and extract the first three numbers
within range [0, 9] that are greater than five. The Nuts example, 
however, is easier to read than the nested itertools code.


For more information on Pythons' itertools see  
https://docs.python.org/2/library/itertools.html  
http://pythonhosted.org/more-itertools/api.html  


# Installation

## Virtual environment

```
$ pip install virtualenv
$ cd my_projects
$ virtualenv vnuts
```

### Activate/Deactivate virtual environment

Linux, Mac:  
```
$ source vnuts/bin/activate
$ deactivate
```

Windows:  
```
> vnuts\Scripts\activate.bat
> vnuts\Scripts\deactivate.bat
```


## Nuts-flow

1) Activate virtual environment (if not already active)
```
cd my_projects
source vnuts/bin/activate
```

2) Clone git repo
```
cd vnuts
git clone git@github.ibm.com:aur/nuts-flow.git
```

3) Install package with dependencies and run unit tests
```
cd nuts-flow
python setup.py install
pytest
```

4) Run Python interpreter and import ```nutsflow``` 
```
python
>>> import nutsflow
>>> nutsflow.__version__
'1.0.1'
exit()
```

5) Try tiny example
```
python
>>> from nutsflow import *
>>> Range(5) >> Square() >> Collect()
[0, 1, 4, 9, 16]
exit()
```
