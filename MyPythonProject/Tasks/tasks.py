# -*- coding: utf-8 -*-
import json
import os
import re
import sys
from contextlib import contextmanager
from itertools import chain
from subprocess import run

from jinja2 import Environment, FileSystemLoader

from Applications.shared import DFTENCODING

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ==========
# Constants.
# ==========
COLUMN = 56


# ==========
# Functions.
# ==========
@contextmanager
def clearscreen():
    run("CLS", shell=True)
    yield


# ===================
# Jinja2 environment.
# ===================
environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Tasks", "Templates"), encoding=DFTENCODING),
                          trim_blocks=True,
                          lstrip_blocks=True,
                          keep_trailing_newline=True)

# ================
# Jinja2 template.
# ===============
template = environment.get_template("T1")

# ====================
# Regular expressions.
# ====================
rex1 = re.compile(r"^\d\d?$")

# ================
# Initializations.
# ================
y, choice = [], 99

# ===============
# Main algorithm.
# ===============

# 1. Load tasks, numbers and return codes.
with open(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Tasks", "Resources", "Tasks.json")) as fp:
    tasks = json.load(fp)

codes = dict([(str(number), code) for task, number, code in tasks])

for item in list(zip(*[iter(tasks)] * 3)):
    menu = ""

    if all(list(chain.from_iterable(item))):
        for task, number, code in item:
            menu = "{2}{0:<{1}}".format("{0:>2d}. {1}".format(number, task), COLUMN, menu)
        y.append(menu)

    if not all(list(chain.from_iterable(item))):

        # Case 1.
        try:
            assert [bool(item) for item in list(zip(*item))[0]] == [True, True, False]
        except AssertionError:
            pass
        else:
            for task, number, code, width in ((task, number, code, width) for (task, number, code), width in zip(item, [COLUMN, COLUMN * 2, 0])):
                if task:
                    menu = "{2}{0:<{1}}".format("{0:>2d}. {1}".format(number, task), width, menu)
            y.append(menu)
            continue

        # Case 2.
        try:
            assert [bool(item) for item in list(zip(*item))[0]] == [True, False, True]
        except AssertionError:
            pass
        else:
            for task, number, code, width in ((task, number, code, width) for (task, number, code), width in zip(item, [COLUMN * 2, 0, COLUMN])):
                if task:
                    menu = "{2}{0:<{1}}".format("{0:>2d}. {1}".format(number, task), width, menu)
            y.append(menu)
            continue

        # Case 3.
        try:
            assert [bool(item) for item in list(zip(*item))[0]] == [True, False, False]
        except AssertionError:
            pass
        else:
            for task, number, code, width in ((task, number, code, width) for (task, number, code), width in zip(item, [COLUMN * 3, 0, 0])):
                if task:
                    menu = "{2}{0:<{1}}".format("{0:>2d}. {1}".format(number, task), width, menu)
            y.append(menu)
            continue

        # Case 4.
        try:
            assert [bool(item) for item in list(zip(*item))[0]] == [False, True, False]
        except AssertionError:
            pass
        else:
            for task, number, code, width in ((task, number, code, width) for (task, number, code), width in zip(item, [0, COLUMN * 2, 0])):
                if task:
                    menu = "{2}{0:>{1}}".format("{0:<{1}}".format("{0:>2d}. {1}".format(number, task), width), COLUMN * 3, menu)
            y.append(menu)
            continue

        # Case 5.
        try:
            assert [bool(item) for item in list(zip(*item))[0]] == [False, False, True]
        except AssertionError:
            pass
        else:
            for task, number, code, width in ((task, number, code, width) for (task, number, code), width in zip(item, [0, 0, COLUMN])):
                if task:
                    menu = "{2}{0:>{1}}".format("{0:<{1}}".format("{0:>2d}. {1}".format(number, task), width), COLUMN * 3, menu)
            y.append(menu)
            continue

        # Case 6.
        try:
            assert [bool(item) for item in list(zip(*item))[0]] == [False, True, True]
        except AssertionError:
            pass
        else:
            for task, number, code, width in ((task, number, code, width) for (task, number, code), width in zip(item, [0, COLUMN, COLUMN])):
                if task:
                    menu = "{2}{0:<{1}}".format("{0:>2d}. {1}".format(number, task), width, menu)
            menu = "{0:>{1}}".format(menu, COLUMN * 3)
            y.append(menu)
            continue

y = ["{0:>{1}}".format(item, len(item) + 8) for item in y]

# 2. Display tasks launcher.
o = template.render(menu=y)
while True:
    with clearscreen():
        print(o)
    choice = input("\t\tPlease enter task: ".expandtabs(4))
    if choice:
        if not rex1.match(choice):
            continue
        if choice not in codes:
            continue
        break
returncode = codes[choice]

# ===============
# Exit algorithm.
# ===============
sys.exit(returncode)
