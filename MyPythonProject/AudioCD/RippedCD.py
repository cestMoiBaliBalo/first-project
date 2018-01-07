# -*- coding: utf-8 -*-
import argparse
import sys

from Applications.Database.AudioCD.shared import insertfromfile

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("tracks", type=argparse.FileType(mode="r", encoding="UTF_8"))

# ================
# Initializations.
# ================
arguments = parser.parse_args()

# ===============
# Main algorithm.
# ===============
sys.exit(insertfromfile(arguments.tracks))
