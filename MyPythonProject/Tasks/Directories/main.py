# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import locale
import os
from collections import Counter
from functools import partial
from itertools import tee
from operator import itemgetter
from pathlib import PureWindowsPath
from typing import List, Optional, Tuple

from Applications.shared import TemplatingEnvironment, count_justify

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

that_file = PureWindowsPath(os.path.abspath(__file__))

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "french")


# ==========
# Functions.
# ==========
def byextension(arg: PureWindowsPath) -> str:
    """

    :param arg:
    :return:
    """
    return arg.suffix


def byname(arg: PureWindowsPath) -> str:
    """

    :param arg:
    :return:
    """
    return arg.stem


def byparents(arg: PureWindowsPath) -> str:
    """

    :param arg:
    :return:
    """
    return str(arg.parents[0])


def rjustify(arg, char: str = " ", length: int = 5) -> str:
    """

    :param arg:
    :param char:
    :param length:
    :return:
    """
    return "{0:{1}>{2}d}".format(arg, char, length)


def valid_extension(path: PureWindowsPath, *, extensions: Optional[Tuple[str, ...]] = None) -> bool:
    """

    :param path:
    :param extensions:
    :return:
    """
    if not extensions:
        return True
    if path.suffix[1:].lower() in [extension.lower() for extension in extensions]:
        return True
    return False


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
collection1, collection2 = [], []  # type: List[PureWindowsPath], List[PureWindowsPath]

# =========
# Template.
# =========
template = TemplatingEnvironment(path=that_file.parents[1] / "Templates", keep_trailing_newline=False)
template.set_environment(filters={"rjustify": rjustify})
template.set_template(template="T01")

# ===============
# Main algorithm.
# ===============
for root, directories, files in os.walk(str(PureWindowsPath(arguments.path))):
    collection1.extend(PureWindowsPath(root) / PureWindowsPath(file) for file in files)
    if not any([directories, files]):
        collection2.extend(PureWindowsPath(root) / PureWindowsPath(directory) for directory in directories)
if arguments.extensions:
    collection1 = list(filter(partial(valid_extension, extensions=tuple(arguments.extensions)), collection1))
collection1 = sorted(sorted(sorted(collection1, key=byname), key=byextension), key=byparents)
it1, it2 = tee(collection1)
_extensions = filter(None, sorted([(key[1:], value) for key, value in count_justify(*Counter(file.suffix for file in it1).items())], key=itemgetter(0)))
_directories = filter(None, sorted([(str(key), value) for key, value in count_justify(*Counter(file.parents[0] for file in it2).items())], key=itemgetter(0)))
print(getattr(template, "template").render(root=arguments.path, files=collection1, extensions=_extensions, directories=_directories, empty_directories=collection2))
