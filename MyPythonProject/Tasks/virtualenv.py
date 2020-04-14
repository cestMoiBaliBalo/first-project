# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, line-too-long
import csv
import locale
import os
import sys
from pathlib import Path

from Applications.shared import ChangeLocalCurrentDirectory, WRITE

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

_ME = Path(os.path.abspath(__file__))
_MYPARENT = Path(os.path.abspath(__file__)).parent

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ==============
# Local classes.
# ==============
class CustomDialect(csv.Dialect):
    delimiter = "|"
    escapechar = "`"
    doublequote = False
    quoting = csv.QUOTE_NONE
    lineterminator = "\r\n"


# ============
# Main script.
# ============

# -----
level = 100

# -----
with ChangeLocalCurrentDirectory(Path(_MYPARENT.parent)):
    collection = list(enumerate([item.name for item in os.scandir("VirtualEnv") if item.is_dir()], start=1))
    collection.append(("99", "Exit"))

# -----
if collection:
    with ChangeLocalCurrentDirectory(Path(os.path.expandvars("%_TMPTXT%")).parent):
        with open(Path(os.path.expandvars("%_TMPTXT%")).name, mode=WRITE, encoding="ISO-8859-1", newline="") as stream:
            csv.writer(stream, dialect=CustomDialect).writerows(collection)
            level = 0

# -----
sys.exit(level)
