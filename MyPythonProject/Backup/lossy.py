# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import csv
import locale
import os
import re
from itertools import chain, compress, filterfalse, groupby
from operator import itemgetter
from pathlib import Path
from typing import Any, List, Tuple

from Applications.callables import match_
from Applications.shared import CustomDialect, TemplatingEnvironment, UTF8, WRITE

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ================
# Local functions.
# ================
def sub_(matchobj) -> str:
    codes = {"ape": 12, "dsf": 15, "flac": 13}
    if matchobj:
        code = codes.get(matchobj.group(3).lower(), matchobj.group(1))
        return f"{code}{matchobj.group(2)}"
    return matchobj.group(0)


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("collection", type=argparse.FileType(encoding=UTF8))
parser.add_argument("commands", type=argparse.FileType(mode=WRITE, encoding="ISO-8859-1"))
arguments = parser.parse_args()

# ============
# Main script.
# ============
REGEX1 = re.compile(r"\b(0[1-9])(\.D[1-9]\.T(?:0[1-9]|[1-5]\d)\.([A-Z0-9]{3,4}))", re.IGNORECASE)
REGEX2 = re.compile(r"\bRECYCLE\b", re.IGNORECASE)
TEMPDIR = Path(os.path.expandvars("%_TMPDIR%"))

# -----
collection = csv.reader(arguments.collection, dialect=CustomDialect)  # type: Any
collection = chain(*[tuple(compress(item, [0, 0, 1, 0, 0])) for item in collection])
collection = list(filterfalse(match_(REGEX2.search), collection))

# -----
ape = [(file, Path(file).parent.parent / "1.Monkey's Audio" / f"{Path(file).stem}.ape") for file in collection]  # type: List[Tuple[str, Path]]
dsf = [(file, Path(file).parent.parent / "1.DSD 64" / f"{Path(file).stem}.dsf") for file in collection]  # type: List[Tuple[str, Path]]
flac = [(file, Path(file).parent.parent / "1.Free Lossless Audio Codec" / f"{Path(file).stem}.flac") for file in collection]  # type: List[Tuple[str, Path]]

# -----
collection = chain.from_iterable([ape, dsf, flac])  # (file1.m4a, file1.ape), (file1.m4a, file1.dsf), (file1.m4a, file1.flac), ...
collection = [(file, Path(REGEX1.sub(sub_, str(path)))) for file, path in collection]  # (file1.m4a, file1.ape), (file1.m4a, file1.dsf), (file1.m4a, file1.flac), ...
collection = [(file, path.exists()) for file, path in collection]  # (file1.m4a, False), (file1.m4a, False), (file1.m4a, True), ...
collection = sorted(collection, key=itemgetter(1))
collection = sorted(collection, key=itemgetter(0))
collection = groupby(collection, key=itemgetter(0))  # (file1.m4a, ((file1.m4a, False), (file1.m4a, False), (file1.m4a, True))), ...
collection = [(key, [exist for _, exist in group]) for key, group in collection]  # (file1.m4a, [False, False, True]), (file2.m4a, [False, False, False]), ...
collection = [Path(file).parent.parent for file, exist in collection if not any(exist)]  # file2.m4a, ...
collection = chain(*[[(path.parent, Path(path.name) / "*" / "*?" / f"*.{extension}", TEMPDIR / "/".join(path.parts[1:])) for extension in ["m4a", "mp3"]] for path in set(collection)])
collection = sorted(collection, key=itemgetter(1))
collection = sorted(collection, key=itemgetter(0))
collection = groupby(collection, key=itemgetter(0))

# -----
environment = TemplatingEnvironment(_MYPARENT.parent / "AudioCD" / "Templates")
arguments.commands.write(environment.get_template("T00c").render(collection=collection, tempdir=TEMPDIR))
