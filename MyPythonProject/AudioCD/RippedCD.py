# -*- coding: utf-8 -*-
import os
import sys
import argparse
from Applications.shared import validdb
from Applications.Database.AudioCD.shared import insertfromfile

__author__ = 'Xavier ROSSET'


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("tracks", type=argparse.FileType(mode="r", encoding="UTF_8"))
parser.add_argument("-d", "--db", dest="database", default=os.path.join(os.path.expandvars("%_COMPUTING%"), "database.db"), type=validdb)


# ================
# Initializations.
# ================
arguments = parser.parse_args()


# ===============
# Main algorithm.
# ===============
sys.exit(insertfromfile(arguments.tracks, db=arguments.database))
