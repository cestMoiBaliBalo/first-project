# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import locale
import os
from collections import Counter
from itertools import tee
from operator import itemgetter
from pathlib import PurePath
from typing import List

from Applications.shared import TemplatingEnvironment, freeze_, pprint_count

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

THAT_FILE = PurePath(os.path.abspath(__file__))

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "french")


# ==========
# Functions.
# ==========
def byextension(arg: PurePath) -> str:
    """

    :param arg:
    :return:
    """
    return arg.suffix


def byname(arg: PurePath) -> str:
    """

    :param arg:
    :return:
    """
    return arg.stem


def byparents(arg: PurePath) -> str:
    """

    :param arg:
    :return:
    """
    return str(arg.parents[0])


def rjustify(arg, *, char: str = " ", length: int = 5) -> str:
    """

    :param arg:
    :param char:
    :param length:
    :return:
    """
    return "{0:{1}>{2}d}".format(arg, char, length)


def valid_extension(path: PurePath, *extensions: str) -> bool:
    """

    :param path:
    :param extensions:
    :return:
    """
    if not extensions:
        return True
    return path.suffix[1:].lower() in (extension.lower() for extension in extensions)


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("path")
parser.add_argument("-e", "--extensions", nargs="*", default=[])
arguments = parser.parse_args()

# ==========
# Variables.
# ==========
collection1, collection2 = [], []  # type: List[PurePath], List[PurePath]

# =========
# Template.
# =========
template = TemplatingEnvironment(THAT_FILE.parents[1] / "Templates", keep_trailing_newline=False, filters={"rjustify": rjustify})

# ===============
# Main algorithm.
# ===============
for root, directories, files in os.walk(str(PurePath(arguments.path))):
    collection1.extend(PurePath(root) / PurePath(file) for file in files)
    if not any([directories, files]):
        collection2.extend(PurePath(root) / PurePath(directory) for directory in directories)
if arguments.extensions:
    collection1 = list(filter(freeze_(arguments.extensions)(valid_extension), collection1))
collection1 = sorted(sorted(sorted(collection1, key=byname), key=byextension), key=byparents)
it1, it2 = tee(collection1)
_extensions = filter(None, sorted([(key[1:], value) for key, value in pprint_count(*Counter(file.suffix for file in it1).items())], key=itemgetter(0)))
_directories = filter(None, sorted([(str(key), value) for key, value in pprint_count(*Counter(file.parents[0] for file in it2).items())], key=itemgetter(0)))
print(template.get_template("T01").render(root=arguments.path, files=collection1, extensions=_extensions, directories=_directories, empty_directories=collection2))
