# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import locale
import os
from collections import Counter
from functools import wraps
from itertools import repeat, tee
from operator import itemgetter
from pathlib import Path
from typing import List, Optional

from Applications.shared import TemplatingEnvironment, pprint_count

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_THATFILE = Path(os.path.abspath(__file__))

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ==========
# Functions.
# ==========
def byextension(arg: Path) -> str:
    """

    :param arg:
    :return:
    """
    return arg.suffix


def byname(arg: Path) -> str:
    """

    :param arg:
    :return:
    """
    return arg.stem


def byparents(arg: Path) -> str:
    """

    :param arg:
    :return:
    """
    return str(arg.parents[0])


def rjustify(arg, *, char: Optional[str] = None, length: int = 5) -> str:
    """

    :param arg:
    :param char:
    :param length:
    :return:
    """
    if char is None:
        return "{0:>{1}d}".format(arg, length)
    return "{0:{1}>{2}d}".format(arg, char, length)


def valid_extension(path: Path, extension: str) -> bool:
    """

    :param path:
    :param extension:
    :return:
    """
    if not extension:
        return True
    return path.suffix[1:].lower() == extension.lower()


# ===========================================
# Callable wrapping valid_extension function.
# ===========================================
def valid_extensions(*extensions: str):
    """

    :param extensions:
    :return:
    """

    @wraps(valid_extension)
    def wrapper(path: Path):
        return any(list(map(valid_extension, repeat(path), extensions)))

    return wrapper


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
collection1, collection2 = [], []  # type: List[Path], List[Path]

# =========
# Template.
# =========
template = TemplatingEnvironment(_THATFILE.parents[1] / "Templates", keep_trailing_newline=False, filters={"rjustify": rjustify})

# ===============
# Main algorithm.
# ===============
for root, directories, files in os.walk(str(Path(arguments.path))):
    collection1.extend(Path(root) / Path(file) for file in files)
    if not any([directories, files]):
        collection2.extend(Path(root) / Path(directory) for directory in directories)
if arguments.extensions:
    collection1 = list(filter(valid_extensions(arguments.extensions), collection1))
collection1 = sorted(sorted(sorted(collection1, key=byname), key=byextension), key=byparents)
it1, it2 = tee(collection1)
_extensions = filter(None, sorted([(key[1:], value) for key, value in pprint_count(*Counter(file.suffix for file in it1).items())], key=itemgetter(0)))
_directories = filter(None, sorted([(str(key), value) for key, value in pprint_count(*Counter(file.parents[0] for file in it2).items())], key=itemgetter(0)))
print(template.get_template("T01").render(root=arguments.path, files=collection1, extensions=_extensions, directories=_directories, empty_directories=collection2))
