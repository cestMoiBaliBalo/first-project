# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import operator
from collections import deque
from functools import wraps
from itertools import chain, islice, tee
from operator import eq, is_
from typing import Any, Tuple

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


def attrgetter_(attr: str):
    """
    That decorator allows to get an object attribute for being used as argument
    by any decorated function.

    :param attr: object attribute name.
    :return: callable object.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg):
            return func(operator.attrgetter(attr)(arg))

        return inner_wrapper

    return outer_wrapper


def eq_(value_first):
    """
    That decorator allows to set the second argument of the function operator.eq
    with the value returned by any decorated function.

    :param value_first: value used to freeze the first positional argument of operator.eq.
    :return: callable object.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg):
            return eq(value_first, func(arg))

        return inner_wrapper

    return outer_wrapper


def int_(base: int = 10):
    """
    That decorator allows to convert a characters string to an integer number
    for being used as argument by any decorated function.

    :param base. decimal base used to perform the conversion. Base 10 is the default value.
    :return: callable object.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg: str):
            return func(int(arg, base=base))

        return inner_wrapper

    return outer_wrapper


def cvtint_(base: int = 10):
    """
    Undocumented.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg: str):
            return int(func(arg), base=base)

        return inner_wrapper

    return outer_wrapper


def itemgetter_(index: int = 0):
    """
    That decorator allows to get a sequence item for being used as argument
    by any decorated function.

    :param index: item index.
    :return: callable object.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg):
            return func(operator.itemgetter(index)(arg))

        return inner_wrapper

    return outer_wrapper


def lower_(func):
    """
    That decorator allows to set to lowercase the result value of any decorated function.

    :return: callable object.
    """

    @wraps(func)
    def wrapper(arg):
        return func(arg).lower()

    return wrapper


def map_(index: int):
    """
    That decorator allows to map any decorated function with all sequences items
    located at index `index`.

    :param index: item index.
    :return: callable object.
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


def none_():
    """
    Undocumented.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg):
            return is_(None, func(arg))

        return inner_wrapper

    return outer_wrapper


def lstrip_(func):
    """
    That decorator allows to strip the left whitespaces from the result value of any decorated function.

    :return: callable object.
    """

    @wraps(func)
    def wrapper(arg):
        return func(arg).lstrip()

    return wrapper


def rstrip_(func):
    """
    That decorator allows to strip the right whitespaces from the result value of any decorated function.

    :return: callable object.
    """

    @wraps(func)
    def wrapper(arg):
        return func(arg).rstrip()

    return wrapper


def split_(char: str):
    """
    That decorator allows to split a characters string for being used as argument
    by any decorated function.

    :param char: character used for processing the splitting.
    :return: callable object.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg: str):
            return func(arg.split(char))

        return inner_wrapper

    return outer_wrapper


def substr_(stop: int, *, start: int = 0):
    """
    Undocumented.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg: str):
            return func(arg)[start:stop]

        return inner_wrapper

    return outer_wrapper
