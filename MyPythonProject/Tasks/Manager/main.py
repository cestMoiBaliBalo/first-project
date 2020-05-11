# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import json
import os
import sys
from pathlib import Path
from subprocess import run
from typing import Any, Mapping

import shared

from Applications.shared import TemplatingEnvironment

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent

# ===================
# Jinja2 environment.
# ===================
environment = TemplatingEnvironment(_MYPARENT.parent / "Templates")

# ============
# Main script.
# ============

# 1. Load actions labels, actions numbers and actions codes.
with open(_MYPARENT.parent / "Resources" / "Menu.json") as fp:
    tasks = json.load(fp)  # type: Any
codes = {str(number): code for _, number, code in tasks}  # type: Mapping[str, int]

# 2. Display menu manager.
menu = environment.get_template("T03").render(collection=list(shared.format_menu(*tasks)))
while True:
    run("CLS", shell=True)
    print(menu)
    choice = input("\t\tPlease enter task: ".expandtabs(4))
    if choice:
        if not shared.REGEX.match(choice):
            continue
        if choice not in codes:
            continue
        break

# ============
# Exit script.
# ============
sys.exit(codes[choice])
