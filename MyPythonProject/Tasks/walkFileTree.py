# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import locale
import os
from collections import Counter
from operator import attrgetter, itemgetter
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

from Applications.callables import filter_extensions, filterfalse_
from Applications.shared import ChangeLocalCurrentDirectory, Files, TemplatingEnvironment, UTF8, WRITE, pprint_count

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ==============
# Local classes.
# ==============
class GetPath(argparse.Action):
    """

    """

    def __init__(self, option_strings, dest, **kwargs):
        super(GetPath, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, Path(values))


# ================
# Local functions.
# ================
def rjustify(arg: int, *, char: Optional[str] = None, length: int = 5) -> str:
    """

    :param arg:
    :param char:
    :param length:
    :return:
    """
    if char is None:
        return "{0:>{length}d}".format(arg, length=length)
    return "{0:{char}>{length}d}".format(arg, char=char, length=length)


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("path", action=GetPath)
parser.add_argument("extensions", nargs="*")
parser.add_argument("--output", type=argparse.FileType(mode=WRITE, encoding=UTF8))
arguments = parser.parse_args()

# ================
# Local constants.
# ================
LETTERS = dict(enumerate(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), start=1))

# ================
# Local variables.
# ================
descendants, content, empty = {}, [], []  # type: Dict[str, int], List[Tuple[str, str, Iterator[Any]]], List[Path]
index = 0  # type: int

# ===============
# Local template.
# ===============
environment = TemplatingEnvironment(_MYPARENT / "Templates", keep_trailing_newline=False, filters={"rjustify": rjustify})

# ============
# Main script.
# ============
excluded = None  # type: Any
if arguments.extensions:
    excluded = filterfalse_(filter_extensions(*arguments.extensions))

# 1. Get files collection.
collection = Files(arguments.path, excluded=excluded)  # type: Any

# 2. Count primary descendants content.
with ChangeLocalCurrentDirectory(arguments.path):
    for directory in os.scandir():
        descendants[str(Path(arguments.path) / directory.name)] = len(Files(Path(directory.name), excluded=excluded))

# Sort files collection.
collection = sorted(collection, key=attrgetter("suffix"))
collection = sorted(collection, key=attrgetter("stem"))
collection = sorted(collection, key=attrgetter("parent"))

# Display argument path content.
if collection:
    index += 1
    content.append(("   ======", f"{LETTERS.get(index, 'Z')}. Files.", iter(collection)))

# Extensions.
extensions = list(filter(None, sorted([f"{key[1:].upper()}: {value}" for key, value in pprint_count(*Counter(file.suffix for file in collection).items())], key=itemgetter(0))))  # type: Any
if extensions:
    index += 1
    content.append(("   ===========", f"{LETTERS.get(index, 'Z')}. Extensions.", iter(extensions)))

# Descendants.
directories = list(filter(None, sorted([f"{str(key)}: {value}" for key, value in pprint_count(*descendants.items())], key=itemgetter(0))))
if directories:
    index += 1
    content.append(("   ============", f"{LETTERS.get(index, 'Z')}. Descendants.", iter(directories)))

# Directories.
directories = list(filter(None, sorted([f"{str(key)}: {value}" for key, value in pprint_count(*Counter(str(file.parent) for file in collection).items())], key=itemgetter(0))))
if directories:
    index += 1
    content.append(("   ============", f"{LETTERS.get(index, 'Z')}. Directories.", iter(directories)))

# Empty directories.
if empty:
    index += 1
    content.append(("   ==================", f"{LETTERS.get(index, 'Z')}. Empty directories.", iter(empty)))

# Store results.
if arguments.output:
    for file in collection:
        arguments.output.write(f"{file}\n")

# Display results.
print(environment.get_template("T06").render(root=str(arguments.path), content=iter(content)))
