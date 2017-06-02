from __future__ import print_function

from six.moves import range, zip
from nutsflow import _
from nutsflow import *


@nut_processor
def MyClone(iterable, n):
    for e in iterable:
        for _ in range(n):
            yield e


@nut_filter
def MyGreaterThan(x, threshold):
    return x > threshold


@nut_filterfalse
def MySmallerOrEqualThan(x, threshold):
    return x > threshold


@nut_source
def MyRange(start, end):
    return iter(range(start, end))


@nut_sink
def MyCollect(iterable):
    return list(iterable)


@nut_function
def MyTimes(x, c):
    return c * x


@nut_processor
def MyPipeline(iterable, func):
    Dup = nut_function(lambda x: (x, x))
    return iterable >> Dup() >> Flatten() >> Map(func)


def run(datapath):
    print(Range(10) >> Shuffle(1) >> Collect())

    print(Range(5) >> MyPipeline(Square()) >> Collect())

    print(MyRange(1, 10) >> MySmallerOrEqualThan(5) >> MyCollect())

    print(MyRange(1, 10) >> MyTimes(3) >> MyGreaterThan(5) >> MyCollect())

    print(MyRange(1, 5) >> MyClone(2) >> MyCollect())

    print(Range(5, 10) >> Zip(Repeat('a')) >> Collect())

    print(Range(10) >> Head(5))

    print(Range(10) >> Tail(5))

    print(Range(10) >> Drop(3) >> Collect())

    print([1, 2, 2, 3, 3, 3] >> CountValues())

    print(Product([1, 2], ['a', 'b']) >> Collect())

    print([1, 2, 3] >> Permutate(2) >> Collect())

    print([1, 2, 3] >> Map(_ * 2) >> Collect())

    print(Range(10) >> Identity() >> Collect())

    print(Range(10) >> Take(5) >> Collect())

    print(range(10) >> TakeWhile(_ < 5) >> Collect())

    print(range(10) >> Filter(_ < 5) >> Collect())

    print(range(10) >> FilterFalse(_ < 5) >> Collect())

    print(range(10) >> Map(_ * 5) >> Collect())

    print('abc' >> Cycle() >> Take(5) >> Collect())

    print('aabacddeaf' >> Dedupe(_ < 'c') >> Collect())

    print(range(10) >> Zip('abcd') >> Collect())

    print(zip([1, 2, 3], 'abc') >> Map(_[::-1]) >> Collect())

    print(range(10) >> Zip('abcd') >> Map(_[0]) >> Collect())

    print(range(10) >> Interleave('abcd') >> Collect())

    print(Empty() >> Collect())

    print(range(20) >> Prefetch() >> Collect())

    with ReadCSV(datapath + 'data.csv') as reader:
        print('data.csv:', reader >> Collect())

    with open(datapath + 'numbers.txt') as f:
        print('numbers.txt:', f >> Collect())

    nums, twos, greater5 = Range(10) >> MapMulti(_, _ * 2, _ > 5)
    nums >> Zip(twos, greater5) >> Print() >> Consume()

    debug = False
    Range(10) >> If(debug, Print()) >> Consume()

    do_square = True
    print(Range(10) >> If(do_square, Square()) >> Collect())

    # numbers = range(100)
    # numbers >> PrintProgress(numbers, 0) >> Sleep(0.1) >> Consume()


if __name__ == '__main__':  # pragma: no cover
    run(r'../../tests/data/')
