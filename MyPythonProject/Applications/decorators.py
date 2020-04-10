# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import operator
import os
from collections import deque
from functools import partial, wraps
from itertools import chain, compress, islice, tee
from pathlib import PurePath
from typing import Any, Tuple

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_THATFILE = PurePath(os.path.abspath(__file__))


def int_(base: int = 10):
    """
    That decorator allows running any function requiring as argument a base 10 integer number when the only available argument is a characters string representing a number.
    The decorator converts the characters string to a base 10 integer number and provides the result to the decorated function.

    ''''''''''''''
    How to use it:
    ''''''''''''''
    @int_()
    def some_callable(arg):
        pass
    1. map(some_callable, [arg1, arg2, arg3, ...]) --> some_callable(int(arg1)), some_callable(int(arg2)), some_callable(int(arg3))
    2. sorted([arg1, arg2, arg3, ...], key=some_callable)

    :param base. decimal base used to perform the conversion.
    :return: callable object.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg: str):
            return func(int(arg, base=base))

        return inner_wrapper

    return outer_wrapper


def attrgetter_(attr: str):
    """
    That decorator allows running any function when the only available argument is an object with attributes.
    The decorator grabs the attribute "attr" and provides it to the decorated function.

    ''''''''''''''
    How to use it:
    ''''''''''''''
    @attrgetter_("some_attribute")
    def some_callable(arg):
        pass
    1. filter(some_callable, [object1, object2, object3, ...]) --> some_callable(object1.some_attribute), some_callable(object2.some_attribute), some_callable(object3.some_attribute)
    2. sorted([object1, object2, object3, ...], key=some_callable)

    :param attr: object attribute name.
    :return: callable object.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg):
            return func(operator.attrgetter(attr)(arg))

        return inner_wrapper

    return outer_wrapper


def itemgetter_(index: int = 0):
    """
    That decorator allows running any function when the only available argument is a sequence.
    The decorator grabs the item located at position "index" and provides it to the decorated function.

    ''''''''''''''
    How to use it:
    ''''''''''''''
    @itemgetter_(2)
    def some_callable(arg):
        pass
    1. filter(some_callable, [sequence1, sequence2, sequence3, ...]) --> some_callable(sequence1[2]), some_callable(sequence2[2]), some_callable(sequence3[2])
    2. sorted([sequence1, sequence2, sequence3, ...], key=some_callable)

    :param index: item index.
    :return: callable object.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg):
            return func(operator.itemgetter(index)(arg))

        return inner_wrapper

    return outer_wrapper


def map_(index: int):
    """

    :param index:
    :return:
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(*iterables: Tuple[Any, ...]):
            it1, it2 = tee(iterables)  # type: Any, Any
            if index > 0:
                collection = deque(iterables)
                collection.rotate(-index)
                it1, it2 = tee(collection)
            obj1 = iter([tuple(map(func, chain(*islice(it1, 1))))])
            obj2 = islice(it2, 1, None)
            collection = chain(obj1, obj2)
            if index > 0:
                collection = deque(collection)
                collection.rotate(index)
                collection = iter(collection)
            for item in collection:
                yield item

        return inner_wrapper

    return outer_wrapper


def compress_(*indexes: int):
    """

    :param indexes:
    :return:
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg: Tuple[Any, ...]):
            selectors = [0] * len(arg)
            for index in indexes:
                selectors[index] = 1
            return func(*compress(arg, selectors))

        return inner_wrapper

    return outer_wrapper


def partial_(*args: Any, **kwargs: Any):
    """

    :param args:
    :param kwargs:
    :return: callable object.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg: Any):
            return partial(func, *args, **kwargs)(arg)

        return inner_wrapper

    return outer_wrapper
