# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import csv
import locale
import os
import sys
from operator import itemgetter
from pathlib import PurePath

from Applications.shared import TemplatingEnvironment

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

that_file = os.path.abspath(__file__)

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
REPOSITORY = os.path.join(os.path.expandvars("%_COMPUTING%"), "counts")

# ==========
# Variables.
# ==========
collection, extensions, status, total = [], [], 0, 0
template = TemplatingEnvironment(path=PurePath(that_file).parent / "Templates")

# ===============
# Main algorithm.
# ===============
template.set_template(template="T02")

with open(f"{REPOSITORY}.csv", encoding="UTF_8", newline="") as stream:
    reader = csv.DictReader(stream)
    for row in reader:
        extensions.append((row["Extensions"], row["Current"], row["Previous"]))

for extension, current, previous in sorted(extensions, key=itemgetter(0)):
    current = int(current)
    previous = int(previous)
    _extension = "{0: <9}".format(extension)
    _current = "{0: >8d}".format(current)
    _previous = "{0: >8d}".format(previous)
    _difference = "{0: >+10d}".format(current - previous)
    total += current - previous
    collection.append((_extension, _current, _previous, _difference))
if arguments.only_differences:
    collection = list(filter(lambda i: itemgetter(3)(i) != 0, collection))
if collection:
    with open(os.path.join(os.path.expandvars("%TEMP%"), "counts.txt"), mode="w", encoding="ISO-8859-1") as stream:
        stream.write(getattr(template, "template").render(collection=[collection, "{0: >+44d}".format(total), arguments.only_differences]))
    status = 1

sys.exit(status)
