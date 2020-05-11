# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import os
import re
import sys
from itertools import chain, zip_longest
from operator import itemgetter
from pathlib import Path
from subprocess import run
from typing import Any, Mapping

import shared

from Applications.callables import match_
from Applications.decorators import itemgetter_
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
collection: Any = sorted(shared.get_targets(Path(os.path.expandvars("%_BACKUP%")) / "workspace.music"), key=itemgetter(0))  # (target1, 1234), (target2, 5678), (target3, 9012), (target4, 3456), ...

# -----
collection1: Any = filter(itemgetter_(0)(match_(re.compile(r"\bspringsteen\b", re.IGNORECASE).search)), collection)  # (target1, 1234), (target2, 5678), ...
collection1 = list(shared.format_collection(*collection1))  # (target1, 1, 1234), (target2, 2, 5678), ...
items1 = len(collection1)

# -----
collection2: Any = filter(itemgetter_(0)(match_(re.compile(r"\bpearl jam\b", re.IGNORECASE).search)), collection)  # (target3, 9012), (target4, 3456), ...
collection2 = list(shared.format_collection(*sorted(collection2, key=itemgetter(0)), start=items1 + 1))  # (target3, 3, 9012), (target4, 4, 3456), ...

# -----
collection = zip_longest(collection1, collection2, fillvalue=(None, None, None))  # ((target1, 1, 1234), (target3, 3, 9012)), ((target2, 2, 5678), (None, None, None)), ...
collection = chain.from_iterable(collection)  # (target1, 1, 1234), (target3, 3, 9012), (target2, 2, 5678), (None, None, None), ...
collection = list(collection)
collection.extend([("Exit", 99, 99), (None, None, None)])

# -----
codes = {str(number): code for _, number, code in collection}  # type: Mapping[str, int]

# -----
menu = environment.get_template("T04").render(collection=list(shared.format_menu(*collection, group=2)))
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
