# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import datetime
import locale
import os
from collections import Counter
from contextlib import suppress
from pathlib import PurePath

import pandas
import yaml

from Applications.shared import ChangeLocalCurrentDirectory, LOCAL, format_date

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
parser.add_argument("path", help="Drive or directory")
arguments = parser.parse_args()

# ==========
# Constants.
# ==========
REPOSITORY = os.path.join(os.path.expandvars("%_COMPUTING%"), "counts")
UPDATE = "r+"
WRITE = "w"

# ==========
# Variables.
# ==========
collection, counts, path, current_counts = [], {}, {}, {}

# ======================
# Get file opening mode.
# ======================
mode = WRITE
if os.path.exists(f"{REPOSITORY}.yml"):
    mode = UPDATE

# ===============
# Main algorithm.
# ===============

#  1. Get collection.
with ChangeLocalCurrentDirectory(PurePath(arguments.path)):
    for root, directories, files in os.walk("."):
        collection.extend([PurePath(file).suffix[1:].upper() for file in files])
collection = list(filter(None, collection))

if collection:

    #  2. Update YML collection.
    path[arguments.path] = dict(Counter(collection))
    counts["Previous"] = {key: 0 for key in Counter(collection).keys()}
    counts["Current"] = dict(Counter(collection))
    with open(f"{REPOSITORY}.yml", mode=mode, encoding="UTF_8") as stream:

        # Get previous collection.
        if mode == UPDATE:
            data = yaml.load(stream)
            _, current_counts = data
            counts["Previous"] = current_counts.get(arguments.path, counts["Previous"])

        # Store current collection.
        with suppress(KeyError):
            del current_counts[arguments.path]
        stream.seek(0)
        stream.truncate()
        yaml.dump([format_date(LOCAL.localize(datetime.datetime.now())), {**path, **current_counts}], stream, indent=2, default_flow_style=False)

    #  3. Update CSV collection.
    counts["Previous"] = pandas.Series(counts["Previous"], index=sorted(counts["Previous"]))
    counts["Current"] = pandas.Series(counts["Current"], index=sorted(counts["Current"]))
    df = pandas.DataFrame(counts)
    df.index.name = "Extensions"
    df.to_csv(f"{REPOSITORY}.csv", encoding="UTF_8")
