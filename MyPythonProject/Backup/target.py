# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import os
from pathlib import Path
from typing import Mapping, Tuple

import yaml

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
        target = mappings.get(arguments.path.relative_to(drive).parts[0].upper(), ())
        for item in target:
            print(item)
