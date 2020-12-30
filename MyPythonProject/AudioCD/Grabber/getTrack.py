# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import csv
import os
import re
import sys
from functools import partial
from itertools import filterfalse
from pathlib import Path
from typing import Any

from Applications.decorators import itemgetter_
from Applications.shared import eq_string_

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent

# ===========
# Main logic.
# ===========
REGEX = re.compile(r"^(\d(\d)?)(/.+)?$")
encoder, tracknumber = "", "0"  # type: str
with open(sys.argv[1], encoding="UTF_16") as stream:
    collection = list(csv.reader(stream, delimiter="=", quoting=csv.QUOTE_NONE, lineterminator="\r\n", doublequote=False))  # type: Any
if collection:
    collection = filterfalse(itemgetter_(0)(partial(eq_string_, "encoder+")), collection)
    collection = dict(collection)
    track = collection.get("Track", collection.get("track"))  # type: str
    match = REGEX.match(track)
    if match:
        tracknumber = match.group(1)
    encoder = collection.get("Encoder", collection.get("encoder", ""))  # type: str
    if encoder:
        encoder = encoder.split()[0]
print(tracknumber)
print(encoder)
