# -*- coding: utf-8 -*-
# pylint: disable=invalid-name

# /volume1/@appstore/py3k/usr/local/bin/python3 /volume1/scripts/myscript.py --test --run
# /volume1/@appstore/py3k/usr/local/bin/python3 /volume1/scripts/myscript.py --run
# copied_20170206_091512.txt
# copied_20170207_090654.txt
# copied_20170210_090836.txt

import argparse
import os
import shutil
import sys
from datetime import datetime

from Modules.shared import DST, SCRIPTS, SRC, subset

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

# =======
# Parser.
# =======
parser = argparse.ArgumentParser()
parser.add_argument("--run", action="store_true")
parser.add_argument("--test", action="store_true")

# ==========
# Constants.
# ==========
COPY = "----------\nCOPY MODE!\n----------\n"
TEST = "----------\nTEST MODE!\n----------\n"

# ===============
# Main algorithm.
# ===============

# ----------
for path in sys.path:
    print(path)

# ----------
arguments = parser.parse_args()
if arguments.run:

    # -----
    src = set(subset(os.listdir(SRC), "*.mp4"))
    dst = set(subset(os.listdir(DST), "*.mp4"))

    # -----
    tobecopied = src.difference(dst)
    if tobecopied:
        with open(os.path.join(SCRIPTS, "copied_{0}.txt".format(datetime.now().strftime("%Y%m%s_%H%M%S"))), "w", encoding="UTF_8") as fw:
            mode = COPY
            if arguments.test:
                mode = TEST
            fw.write(mode)
            for video in sorted(tobecopied):
                fw.write("{0}\n".format(os.path.join(SRC, video)))
                if not arguments.test:
                    shutil.copy(os.path.join(SRC, video), DST)
