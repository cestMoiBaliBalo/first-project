# -*- coding: utf-8 -*-
from Applications.shared import rjustify, DFTENCODING
from jinja2 import Environment, FileSystemLoader
from contextlib import contextmanager
from collections import namedtuple
from subprocess import run
import json
import sys
import os
import re

__author__ = 'Xavier ROSSET'


# ==========
# Constants.
# ==========
TASKS = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Tasks", "Tasks.json")
COLUMN = 56
SPACES = 5


# ==========
# Functions.
# ==========
@contextmanager
def clearscreen():
    run("CLS", shell=True)
    yield


def rtabulate(s, l=COLUMN, tab=4):
    if len(s) >= l:
        return s
    t = (l - len(s))//tab
    if (l - len(s)) % tab:
        t += 1
    return "{0}{1}".format(s, "\t"*t).expandtabs(tab)


# ===================
# Jinja2 environment.
# ===================
environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Tasks", "Templates"), encoding=DFTENCODING),
                          trim_blocks=True,
                          lstrip_blocks=True,
                          keep_trailing_newline=True)


# ======================
# Jinja2 custom filters.
# ======================
environment.filters["rtabulate"] = rtabulate
environment.filters["rjustify"] = rjustify


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
choice, returncode, Task = 99, 100, namedtuple("Task", "title number length")


# ===============
# Main algorithm.
# ===============

# 1. Load tasks, numbers and return codes.
with open(TASKS) as fp:
    data = json.load(fp)
    tasks = [Task(title, str(number), len(title) + SPACES) for title, number, code in data]
    codes = dict([(str(number), code) for title, number, code in data])

# 2. Display tasks launcher.
if all([tasks, codes]):
    o = template.render(tasks=tasks, column=COLUMN)
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
