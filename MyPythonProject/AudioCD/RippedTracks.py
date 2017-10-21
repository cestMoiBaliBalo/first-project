# -*- coding: utf-8 -*-
import argparse
import sys
from itertools import accumulate

from Applications.Database.DigitalAudioFiles.shared import insertfromfile
from Applications.parsers import database_parser

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser(parents=[database_parser])
parser.add_argument("tracks", type=argparse.FileType(mode="r", encoding="UTF_8"))

# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":
    arguments = parser.parse_args()
    sys.exit(list(accumulate(insertfromfile(arguments.tracks, db=arguments.db)))[-1])
