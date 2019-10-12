# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import csv
import locale
import os
import sys
from functools import partial
from itertools import filterfalse
from operator import eq, itemgetter
from pathlib import PurePath

from Applications.shared import TemplatingEnvironment, itemgetter_

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_THATFILE = os.path.abspath(__file__)

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "french")

# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("--only_differences", "-d", action="store_true")
arguments = parser.parse_args()

# ==========
# Constants.
# ==========
REPOSITORY = str(PurePath(os.path.expandvars("%_COMPUTING%")) / "counts")

# ==========
# Variables.
# ==========
collection, extensions, status, total = [], [], 1, 0
template = TemplatingEnvironment(PurePath(_THATFILE).parents[1] / "Templates")

# ===============
# Main algorithm.
# ===============
with open(f"{REPOSITORY}.csv", encoding="UTF_8", newline="") as stream:
    reader = csv.DictReader(stream)
    for row in reader:
        extensions.append((row["Extensions"], row["Current"], row["Previous"]))

for extension, current, previous in sorted(extensions, key=itemgetter(0)):
    current = int(current)
    previous = int(previous)
    _extension = "{0:<9}".format(extension)
    _current = "{0:>8d}".format(current)
    _previous = "{0:>8d}".format(previous)
    _difference = "{0:>+10d}".format(current - previous)
    total += current - previous
    collection.append((_extension, _current, _previous, _difference, current - previous))
if arguments.only_differences:
    collection = list(filterfalse(itemgetter_(4)(partial(eq, 0)), collection))
if collection:
    status = 0
    with open(os.path.join(os.path.expandvars("%TEMP%"), "counts.txt"), mode="w", encoding="ISO-8859-1") as stream:
        stream.write(template.get_template("T02").render(collection=[collection, "{0:>+44d}".format(total), arguments.only_differences]))

sys.exit(status)
