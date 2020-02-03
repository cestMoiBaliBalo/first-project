# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import operator
import os
from functools import partial, wraps
from itertools import compress
from pathlib import PurePath
from typing import Any, Tuple

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_THATFILE = PurePath(os.path.abspath(__file__))


def attrgetter_(attr: str):
    """
    That decorator allows running any function using as argument an object attribute named `attribute`.
    It must be used everywhere a callable object with an object as argument is required.

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
    That decorator allows running any function using as argument a sequence item located at index `index`.
    It must be used everywhere a callable object with a sequence as argument is required.

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


def int_(base: int = 10):
    """


    ''''''''''''''
    How to use it:
    ''''''''''''''
    @int_()
    def some_callable(arg):
        pass
    1. map(some_callable, [arg1, arg2, arg3, ...]) --> some_callable(int(arg1)), some_callable(int(arg2)), some_callable(int(arg3))
    2. sorted([arg1, arg2, arg3, ...], key=some_callable)

    :param base.
    :return: callable object.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg: str):
            return func(int(arg, base=base))

        return inner_wrapper

    return outer_wrapper


def compress_(*indexes: int):
    """

    :param indexes:
    :return:
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg: Tuple[Any]):
            selectors = [0] * len(arg)
            for index in indexes:
                selectors[index] = 1
            return func(*compress(arg, selectors))

        return inner_wrapper

    return outer_wrapper


def map_(index: int):
    """

    :param index:
    :return:
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(*args: Any):
            iterable = tuple(args)
            if 0 < index < len(args) - 1:
                iterable = args[:index] + (func(operator.itemgetter(index)(args)),) + args[index + 1:]
            elif index == 0:
                iterable = (func(operator.itemgetter(index)(args)),) + args[index + 1:]
            elif index == len(args) - 1:
                iterable = args[:index] + (func(operator.itemgetter(index)(args)),)
            return iter(iterable)

        return inner_wrapper

    return outer_wrapper


def nested_(*functions):
    """

    :param functions: sequence of callables.
    :return: callable object.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg):
            returned = func(arg)
            for function in functions:
                returned = function(returned)
            return returned

        return inner_wrapper

    return outer_wrapper


def partial_(*args, **kwargs):
    """

    :param args:
    :param kwargs:
    :return: callable object.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg):
            return partial(func, *args, **kwargs)(arg)

        return inner_wrapper

    return outer_wrapper
