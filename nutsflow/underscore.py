"""
.. module:: underscore
   :synopsis: Enables underscore to be used as anonymous variable.
"""
from __future__ import division

from functools import partial, wraps
import operator as op


def _wrap(func, args, flip=True):
    """Return partial function with flipped args if flip=True

    :param function func: Any function
    :param args args: Function arguments
    :param bool flip: If true reverse order of arguments.
    :return: Returns function
    :rtype: function
    """

    @wraps(func)
    def flippedfunc(*args):
        return func(*args[::-1])

    return partial(flippedfunc if flip else func, args)


# TODO: support len(_), (_ in 'test'), (_ + _) and similar constructs
class _Underscore(object):
    """
    Placeholder class for anonymous variables. Allows constructs such as:

    >>> list(map(_ * 2, range(5)))
    [0, 2, 4, 6, 8]

    >>> list(filter(_ < 3, range(5)))
    [0, 1, 2]
    """

    __call__ = lambda self, arg: arg
    __add__ = lambda self, arg: _wrap(op.add, arg)
    __radd__ = lambda self, arg: _wrap(op.add, arg, False)
    __sub__ = lambda self, arg: _wrap(op.sub, arg)
    __rsub__ = lambda self, arg: _wrap(op.sub, arg, False)
    __mul__ = lambda self, arg: _wrap(op.mul, arg)
    __rmul__ = lambda self, arg: _wrap(op.mul, arg, False)
    __truediv__ = lambda self, arg: _wrap(op.truediv, arg)
    __rtruediv__ = lambda self, arg: _wrap(op.truediv, arg, False)
    __floordiv__ = lambda self, arg: _wrap(op.floordiv, arg)
    __rfloordiv__ = lambda self, arg: _wrap(op.floordiv, arg, False)
    __mod__ = lambda self, arg: _wrap(op.mod, arg)
    __rmod__ = lambda self, arg: _wrap(op.mod, arg, False)

    __eq__ = lambda self, arg: _wrap(op.eq, arg)
    __ne__ = lambda self, arg: _wrap(op.ne, arg)
    __lt__ = lambda self, arg: _wrap(op.lt, arg)
    __le__ = lambda self, arg: _wrap(op.le, arg)
    __gt__ = lambda self, arg: _wrap(op.gt, arg)
    __ge__ = lambda self, arg: _wrap(op.ge, arg)

    __getitem__ = lambda self, arg: _wrap(op.getitem, arg)


_ = _Underscore()
