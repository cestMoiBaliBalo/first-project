# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import csv
import itertools
import os
from contextlib import ExitStack
from pathlib import Path

from Applications.shared import TemplatingEnvironment, itemgetter_

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_THATFILE = Path(os.path.abspath(__file__))


# ========
# Classes.
# ========
class CustomDialect(csv.Dialect):
    def __init__(self, delimiter="|", escapechar="`", doublequote=False, quoting=csv.QUOTE_NONE, lineterminator="\r\n"):
        super(CustomDialect, self).__init__()
        self.delimiter = delimiter
        self.escapechar = escapechar
        self.doublequote = doublequote
        self.quoting = quoting
        self.lineterminator = lineterminator


# ==========
# Functions.
# ==========
@itemgetter_()
def get_parent(path: str) -> Path:
    return Path(path).parent


@itemgetter_()
def get_name(path: str) -> str:
    return Path(path).name


# ==========
# Constants.
# ==========
COMPUTING = Path(os.path.expandvars("%_COMPUTING%"))
RIPPEDTRACKS = "rippedtracks"

# ============
# Main script.
# ============

# Define template.
template = TemplatingEnvironment(_THATFILE.parents[1] / "Templates")

# Set copy commands file.
with ExitStack() as stack:
    fr = stack.enter_context(open(COMPUTING / "Resources" / f"{RIPPEDTRACKS}.txt", encoding="UTF_8", newline=""))
    fw = stack.enter_context(open(COMPUTING / "Resources" / f"{RIPPEDTRACKS}.cmd", mode="w", encoding="ISO-8859-1"))
    reader = csv.reader(fr, dialect=CustomDialect())
    tracks = sorted(sorted(filter(None, reader), key=get_name), key=get_parent)
    tracks = [(src, Path(src).name, dst) for src, dst in tracks]
    fw.write(template.get_template("T02").render(collection=iter((key, list(group)) for key, group in itertools.groupby(tracks, key=get_parent))))
