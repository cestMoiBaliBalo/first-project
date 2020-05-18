# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import os
import re
from contextlib import ExitStack
from itertools import chain, compress, count, starmap, zip_longest
from pathlib import Path
from typing import Any, Iterator, Optional, Tuple

from lxml import etree  # type: ignore

from Applications.shared import UTF8

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYPARENT = Path(os.path.abspath(__file__)).parent

# ====================
# Regular expressions.
# ====================
REGEX = re.compile(r"^\d\d?$")


# =================
# Shared functions.
# =================
def format_collection(*iterables, start: int = 1) -> Iterator[Tuple[str, int, str]]:
    """

    :param iterables:
    :param start:
    :return:
    """
    _collection = zip(iterables, count(start))  # ((target1, 1234), 1), ((target2, 5678), 2), ...
    _collection = [tuple(chain(*[target], (number,))) for target, number in _collection]  # (target1, 1234, 1), (target2, 5678, 2), ...
    _collection = [tuple(compress(_item, [1, 0, 0])) + tuple(map(int, compress(_item, [0, 0, 1]))) + tuple(compress(_item, [0, 1, 0])) for _item in _collection]  # type: Any
    for _item in _collection:
        yield _item


def format_menu(*iterables, group=3) -> Iterator[str]:
    """

    :param iterables:
    :param group:
    :return:
    """
    _collection: Any = [tuple(compress(_item, [1, 1, 0])) for _item in iterables]  # ("menu1", 1), ("menu2", 2), (None, None), ...
    _collection = starmap(_format1, _collection)  # " 1. menu1", " 2. menu2", "", ...
    _collection = zip_longest(*[_collection] * group)  # (" 1. menu1", " 2. menu2", ""), ...
    _collection = [tuple(map(_format2, _item)) for _item in _collection]  # (" 1. menu1     ", " 2. menu2     ", "          "), ...
    _collection = ["".join(_item) for _item in _collection]  # " 1. menu1      2. menu2               ", ...
    for _item in _collection:
        yield _item


def get_targets(path):
    """

    :param path:
    :return:
    """
    with ExitStack() as stack:
        targets = [stack.enter_context(open(entry, encoding=UTF8)) for entry in os.scandir(Path(path)) if entry.is_file()]
        for target in targets:
            tree = etree.parse(target)
            root = tree.xpath("/target")[0]
            yield root.get("name"), int(root.get("uid"))


# ==================
# Private functions.
# ==================
def _format1(label: Optional[str], number: Optional[int]) -> str:
    """

    :param label:
    :param number:
    :return:
    """
    if all([number, label]):
        return "{0:>2d}. {1}".format(number, label)
    return ""


def _format2(arg: str, *, width: int = 56) -> str:
    """

    :param arg:
    :param width:
    :return:
    """
    return "{0:<{width}}".format(arg, width=width)
