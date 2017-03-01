"""
.. module:: test_common
   :synopsis: Unit tests for common module
"""

from nutsflow.common import sec_to_hms, timestr, Redirect, as_tuple, as_set


def test_as_tuple():
    assert as_tuple(1) == (1,)
    assert as_tuple((1, 2)) == (1, 2)
    assert as_tuple([1, 2]) == (1, 2)


def test_as_set():
    assert as_set(1) == (1,)
    assert as_set((1, 2)) == {1, 2}
    assert as_set([1, 2]) == {1, 2}


def test_sec_to_hms():
    assert sec_to_hms('80') == (0, 1, 20)
    assert sec_to_hms(3 * 60 * 60 + 2 * 60 + 1) == (3, 2, 1)


def test_timestr():
    assert timestr('') == ''
    assert timestr('80') == '0:01:20'


def test_Redirect():
    with Redirect() as out:
        print 'test'
    assert out.getvalue() == 'test\n'
