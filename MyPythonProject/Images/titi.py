# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import json
import locale
import os
import sys

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

that_file = os.path.abspath(__file__)

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "french")

# ================
# Initializations.
# ================
_commands, _year = [], sys.argv[1]
_root = os.path.join(r"\\diskstation\backup\images\collection", _year)
_indexes = os.path.join(os.path.expandvars("%TEMP%"), "index.json")

# ===================
# Load configuration.
# ===================
with open(_indexes, encoding="UTF_8") as stream:
    cfg = json.load(stream)
index = cfg.get(_year, 0)

for month in sorted(os.listdir(_root)):
    root = os.path.join(_root, month)
    for path, _, files in sorted(os.walk(root)):
        for file in filter(lambda item: os.path.splitext(item)[1].lower() == ".jpg", files):
            index += 1
            _commands.append((os.path.join(path, file), "{1}_{0:>05d}.jpg".format(index, _year)))

with open(os.path.join(os.path.expandvars("%TEMP%"), "toto.cmd"), "w", encoding="ISO-8859-1") as stream:
    for file, new_name in _commands:
        stream.write(f'\nRENAME "{file}" "{new_name}"')

with open(_indexes, "w", encoding="UTF_8") as stream:
    cfg[_year] = index
    json.dump(cfg, stream)
