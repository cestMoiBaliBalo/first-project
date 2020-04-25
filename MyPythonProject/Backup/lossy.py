# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import csv
import locale
import os
import re
from itertools import chain, compress, groupby, tee
from operator import itemgetter
from pathlib import Path
from tempfile import mkdtemp
from typing import Any, Iterator, Tuple

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
REGEX = re.compile(r"\b(0[1-9])(\.D[1-9]\.T(?:0[1-9]|[1-5]\d)\.([A-Z0-9]{3,4}))", re.IGNORECASE)
TEMPDIR = Path(mkdtemp())

# -----
collection = csv.reader(arguments.collection, dialect=CustomDialect)
collection = chain(*iter(tuple(compress(item, [0, 0, 1, 0, 0])) for item in collection))  # type: Any

# -----
it1, it2, it3 = tee(collection, 3)
ape = iter((file, Path(file).parent.parent / "1.Monkey's Audio" / f"{Path(file).stem}.ape") for file in it1)  # type: Iterator[Tuple[str, Path]]
dsf = iter((file, Path(file).parent.parent / "1.DSD 64" / f"{Path(file).stem}.dsf") for file in it2)  # type: Iterator[Tuple[str, Path]]
flac = iter((file, Path(file).parent.parent / "1.Free Lossless Audio Codec" / f"{Path(file).stem}.flac") for file in it3)  # type: Iterator[Tuple[str, Path]]

# -----
collection = chain.from_iterable([ape, dsf, flac])  # (file1.m4a, file1.ape), (file1.m4a, file1.dsf), (file1.m4a, file1.flac), ...
collection = iter((file, Path(REGEX.sub(sub_, str(path)))) for file, path in collection)  # (file1.m4a, file1.ape), (file1.m4a, file1.dsf), (file1.m4a, file1.flac), ...
collection = iter((file, path.exists()) for file, path in collection)  # (file1.m4a, False), (file1.m4a, False), (file1.m4a, True), ...
collection = sorted(collection, key=itemgetter(1))
collection = sorted(collection, key=itemgetter(0))
collection = groupby(collection, key=itemgetter(0))  # (file1.m4a, Iterator[(file1.m4a, False), (file1.m4a, False), (file1.m4a, True)]), ...
collection = iter((key, iter(exist for _, exist in group)) for key, group in collection)  # (file1.m4a, Iterator[(False, False, True)]), (file2.m4a, Iterator[(False, False, False)]), ...
collection = iter(Path(file).parent.parent for file, exist in collection if not any(exist))  # file2.m4a, ...
collection = chain(*iter([(path.parent, Path(path.name) / "*" / "*?" / f"*.{extension}", TEMPDIR / "/".join(path.parts[1:])) for extension in ["m4a", "mp3"]] for path in set(collection)))
collection = sorted(collection, key=itemgetter(1))
collection = sorted(collection, key=itemgetter(0))
# print(list(collection))
collection = groupby(collection, key=itemgetter(0))

# -----
template = TemplatingEnvironment(_MYPARENT.parent / "AudioCD" / "Templates")
arguments.commands.write(template.get_template("T00c").render(collection=collection, tempdir=TEMPDIR))
