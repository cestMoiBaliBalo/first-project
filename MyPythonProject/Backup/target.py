# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import os
from contextlib import ExitStack
from pathlib import Path
from typing import Mapping, Tuple

import yaml

from Applications.shared import WRITE

__author__ = "Xavier ROSSET"
__maintainer__ = "Xavier ROSSET"
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYPARENT = Path(os.path.abspath(__file__)).parent


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
parser.add_argument("output", type=argparse.FileType(mode=WRITE, encoding="ISO-8859-1"))
arguments = parser.parse_args()

# ============
# Main script.
# ============

# -----
drive = f"{arguments.path.drive}/"

# -----
mapping = {}  # type: Mapping[str, Tuple[str, str]]
with open(_MYPARENT / "targets.yml", encoding="UTF_8") as stream:
    mappings = yaml.load(stream, Loader=yaml.FullLoader)
    if mappings:
        target = mappings.get(arguments.path.relative_to(drive).parts[0].upper())
        if target:
            arguments.output.write("{0}\n".format("|".join(target)))
