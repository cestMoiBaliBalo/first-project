# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import operator
from collections import deque
from functools import wraps
from itertools import chain, islice, tee
from operator import contains, eq, is_
from typing import Any, Tuple

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# =====================
# Decorators factories.
# =====================
def attrgetter_(attr: str):
    """
    Decorators factory.
    Make a decorator that grabs, from any object argument, the attribute with the name `attr`.
    The grabbed value is then used by the decorated function.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg):
            return func(operator.attrgetter(attr)(arg))

        return inner_wrapper

    return outer_wrapper


def itemgetter_(index: int = 0):
    """
    Decorators factory.
    Make a decorator that grabs, from any iterable argument, the item with the index `index`.
    The grabbed value is then used by the decorated function.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg):
            return func(operator.itemgetter(index)(arg))

        return inner_wrapper

    return outer_wrapper


def contains_(*args):
    """
    Decorators factory.
    Make a decorator that sets any function return value as the second argument
    for the function `operator.contains`.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg):
            return contains(args, func(arg))

        return inner_wrapper

    return outer_wrapper


def eq_(value_first):
    """
    Decorators factory.
    Make a decorator that sets any function return value as the second argument
    for the function `operator.eq`.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg):
            return eq(value_first, func(arg))

        return inner_wrapper

    return outer_wrapper


def cvtint_(base: int = 10):
    """
    Decorators factory.
    Make a decorator that sets any function return value as argument
    for the builtin function `int`.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg: str):
            return int(func(arg), base=base)

        return inner_wrapper

    return outer_wrapper


def int_(base: int = 10):
    """
    Decorators factory.
    Make a decorator that maps any argument to an integer number.
    The mapped value is then used by the decorated function.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg: str):
            return func(int(arg, base=base))

        return inner_wrapper

    return outer_wrapper


def slice_(*args):
    """
    Decorators factory.
    Make a decorator that sets any function return value as the first argument
    for the function `itertools.islice`.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg: str):
            return "".join(islice(func(arg), *args))

        return inner_wrapper

    return outer_wrapper


def map_(index: int):
    """
    Decorators factory.
    Make a decorator that maps with the decorated function any item from an iterable argument with the index `index`.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(*iterables: Tuple[Any, ...]):
            it1, it2 = tee(zip(*iterables))  # type: Any, Any
            if index > 0:
                collection = deque(zip(*iterables))  # type: Any
                collection.rotate(-index)
                it1, it2 = tee(collection)
            collection = zip(map(func, chain(*islice(it1, 1))), *islice(it2, 1, None))
            if index > 0:
                collection = [deque(item) for item in collection]
                for item in collection:
                    item.rotate(index)
                collection = [tuple(item) for item in collection]
            for item in collection:
                yield item

        return inner_wrapper

    return outer_wrapper


def split_(char: str):
    """
    Decorators factory.
    Make a decorator that splits any string argument into a list.
    The returned list is then used by the decorated function.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg: str):
            return func(arg.split(char))

        return inner_wrapper

    return outer_wrapper


# ===========
# Decorators.
# ===========
def none_(func):
    """
    Decorator that sets any function return value as the second argument
    for the function `operator.is_`.
    The first argument is frozen to `None`.
    """

    @wraps(func)
    def wrapper(arg):
        return is_(None, func(arg))

    return wrapper


def lower_(func):
    """
    Decorator that sets to lowercase any function return value.
    """

    @wraps(func)
    def wrapper(arg):
        return func(arg).lower()

    return wrapper


def lstrip_(func):
    """
    Decorator that removes left spaces from any function return value.
    """

    @wraps(func)
    def wrapper(arg):
        return func(arg).lstrip()

    return wrapper


def rstrip_(func):
    """
    Decorator that removes right spaces from any function return value.
    """

    @wraps(func)
    def wrapper(arg):
        return func(arg).rstrip()

    return wrapper
