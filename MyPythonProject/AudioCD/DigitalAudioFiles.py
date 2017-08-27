# -*- coding: ISO-8859-1 -*-
import argparse
import json
import os

__author__ = 'Xavier ROSSET'


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("inpfile")


# ==========
# Constants.
# ==========
JSON = os.path.join(os.path.expandvars("%TEMP%"), "files.json")


# ================
# Initializations.
# ================
obj, arguments = list(), parser.parse_args()


# ===============
# Main algorithm.
# ===============
if os.path.exists(JSON):
    with open(JSON, encoding="UTF_8") as fp:
        obj = json.load(fp)
obj.append(arguments.inpfile)
with open(JSON, mode="w", encoding="UTF_8") as fp:
    json.dump(list(set(obj)), fp, indent=4, sort_keys=True, ensure_ascii=False)


