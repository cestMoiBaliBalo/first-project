# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import os
import sys
from contextlib import ExitStack
from pathlib import Path
from typing import Mapping, Tuple

import yaml

from Applications.shared import TEMP, WRITE

__author__ = "Xavier ROSSET"
__maintainer__ = "Xavier ROSSET"
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_THATFILE = Path(os.path.abspath(__file__))


# ==============
# Local classes.
# ==============
class GetPath(argparse.Action):
    """

    """

    def __init__(self, option_strings, dest, **kwargs):
        super(GetPath, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, Path(values))


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("path", action=GetPath)
arguments = parser.parse_args()

# ============
# Main script.
# ============
tmpfil = Path(os.path.expandvars("%_TMPDIR%")) / os.path.expandvars("%_TMPTXT%")  # type: Path

# -----
drive = f"{arguments.path.drive}/"

# -----
mapping = {}  # type: Mapping[str, Tuple[str, str]]
stack = ExitStack()
rea_stream = stack.enter_context(open(_THATFILE.parent / "targets.yml", encoding="UTF_8"))
wrt_stream = stack.enter_context(open(tmpfil, mode=WRITE, encoding="ISO-8859-1"))
with stack:
    mappings = yaml.load(rea_stream, Loader=yaml.FullLoader)
    if mappings:
        target = mappings.get(arguments.path.relative_to(drive).parts[0].upper())
        if target:
            wrt_stream.write("{0}\n".format("|".join(target)))
