"""
.. module:: examples
   :synopsis: Unit tests for examples module
"""
import nutsflow.examples.examples as examples

from nutsflow.common import Redirect


# Just check that examples are not crashing.
def test_run_examples():
    with Redirect() as out:
        examples.run('tests/data/')
        assert out.getvalue()
