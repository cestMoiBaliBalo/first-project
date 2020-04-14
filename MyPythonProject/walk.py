# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import locale
import os
import re
from collections import Counter
from collections import defaultdict
from operator import itemgetter
from pathlib import Path
from typing import Any, DefaultDict, Iterator, List, Optional, Tuple

from Applications.callables import match_
from Applications.shared import ChangeLocalCurrentDirectory, TemplatingEnvironment, UTF8, WRITE, pprint_count

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYPARENT = Path(os.path.abspath(__file__)).parent

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ==============
# Local classes.
# ==============
class CompilePattern(argparse.Action):
    """

    """

    def __init__(self, option_strings, dest, **kwargs):
        super(CompilePattern, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        setattr(namespace, "regex", re.compile(values, re.IGNORECASE))


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


def byparent(arg: Path) -> str:
    """

    :param arg:
    :return:
    """
    return str(arg.parent)


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


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("path", action=GetPath)
parser.add_argument("--pattern", action=CompilePattern)
parser.add_argument("--output", type=argparse.FileType(mode=WRITE, encoding=UTF8))
arguments = parser.parse_args()

# ================
# Local variables.
# ================
collection1, collection2, content = [], [], []  # type: List[Path], List[Path], List[Tuple[str, str, str, Iterator[Any]]]
index = 0  # type: int
children = defaultdict(int)  # type: DefaultDict[Path, int]

# ===============
# Local template.
# ===============
template = TemplatingEnvironment(_MYPARENT, keep_trailing_newline=False, filters={"rjustify": rjustify})

# ============
# Main script.
# ============
LETTERS = dict(enumerate(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), start=1))

with ChangeLocalCurrentDirectory(arguments.path):

    # 1. Walk through argument path.
    for root, directories, files in os.walk("."):

        # Get files.
        collection1.extend((Path(root) / file).resolve() for file in files)

        # Get empty directories.
        if not any([directories, files]):
            collection2.append(Path(root))

    # 2. Walk through descendants of argument path.
    for directory in os.scandir("."):
        for _, _, files in os.walk(directory.path):
            if arguments.pattern:
                files = list(filter(match_(arguments.regex.match), files))
            children[Path(directory.path).resolve()] += len(files)

# Filter files collection.
if arguments.pattern:
    collection1 = list(map(Path, filter(match_(arguments.regex.match), map(str, collection1))))

# Sort files collection.
collection1 = sorted(sorted(sorted(collection1, key=byname), key=byextension), key=byparent)

# Display argument path content.
if collection1:
    index += 1
    content.append(("   ======", f"{LETTERS.get(index, 'Z')}. Files.", "   ======", iter(collection1)))

# Extensions.
_extensions = list(filter(None, sorted([f"{key[1:].upper()}: {value}" for key, value in pprint_count(*Counter(file.suffix for file in collection1).items())], key=itemgetter(0))))  # type: Any
if _extensions:
    index += 1
    content.append(("   ===========", f"{LETTERS.get(index, 'Z')}. Extensions.", "   ===========", iter(_extensions)))

# Directories.
_directories = list(filter(None, sorted([f"{str(key)}: {value}" for key, value in pprint_count(*children.items())], key=itemgetter(0))))  # type: Any
if _directories:
    index += 1
    content.append(("   ============", f"{LETTERS.get(index, 'Z')}. Directories.", "   ============", iter(_directories)))

# Detailed directories.
_directories = list(filter(None, sorted([f"{str(key)}: {value}" for key, value in pprint_count(*Counter(str(file.parent) for file in collection1).items())], key=itemgetter(0))))
if _directories:
    index += 1
    content.append(("   =====================", f"{LETTERS.get(index, 'Z')}. Detailed directories.", "   =====================", iter(_directories)))

# Empty directories.
if collection2:
    index += 1
    content.append(("   ==================", f"{LETTERS.get(index, 'Z')}. Empty directories.", "   ==================", iter(collection2)))

# Store results.
if arguments.output:
    for file in collection1:
        arguments.output.write(f"{file}\n")

# Display results.
print(template.get_template("walk.tpl").render(root=str(arguments.path), content=iter(content)))
