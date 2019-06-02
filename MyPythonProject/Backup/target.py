# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import os
import sys
from contextlib import ExitStack
from pathlib import PurePath

import yaml

__author__ = "Xavier ROSSET"
__maintainer__ = "Xavier ROSSET"
__email__ = "xavier.rosset@eugeneperma.fr"
__status__ = "Production"


# ==========
# Constants.
# ==========
SRC = PurePath(os.path.expandvars("%_PYTHONPROJECT%")) / "Backup"
DST = PurePath(os.path.expandvars("%TEMP%"))

# ===============
# Main algorithm.
# ===============
mapping = {}
stack = ExitStack()
rea_stream = stack.enter_context(open(SRC / "targets.yml", encoding="UTF_8"))
upd_stream = stack.enter_context(open(DST / "target.txt", mode="w", encoding="ISO-8859-1"))
with stack:
    mappings = yaml.load(rea_stream)
    if mappings:
        upd_stream.write("{0}\n".format(mappings.get(PurePath(sys.argv[1]).parts[-1][0].upper(), 0)))
