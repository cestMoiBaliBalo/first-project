# -*- coding: utf-8 -*-
"""
Display audio folders content.
Called from tasks manager "tasks.cmd". Option "35".
"""
# pylint: disable=invalid-name
import locale
import logging.config
import os
import re
import sys
from contextlib import ExitStack
from itertools import groupby, repeat
from subprocess import run

import jinja2
import yaml

from Applications.shared import ChangeLocalCurrentDirectory, MUSIC, TemplatingEnvironment, cjustify, rjustify

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))


# ==========
# Functions.
# ==========
def init():
    return MUSIC, 1, False, False, [], []


def get_folders(directory):
    _collection = []
    stack = ExitStack()
    try:
        stack.enter_context(ChangeLocalCurrentDirectory(directory))
    except PermissionError:
        pass
    else:
        with stack:
            _collection = [(name, os.path.join(os.getcwd(), name)) for name in os.listdir(".")]
    for name, path in _collection:
        yield name, path


def pprint_extensions(*iterable):
    # Left justify keys.
    keys = list(zip(*iterable))[0]
    length = max(len(key) for key in keys)
    keys = ["{0:<{1}}".format(key, length) for key in keys]

    # Right justify pairs.
    pairs = list(zip(*iterable))[1]
    length = max(len(str(pair)) for pair in pairs)
    pairs = ["{0:>{1}}".format(pair, length) for pair in pairs]

    for key, pair in zip(keys, pairs):
        yield key, pair


def pprint_files(*iterable, length=229):
    keys = list(zip(*iterable))[0]
    pairs = list(zip(*iterable))[1]
    pairs = ["{0:n}".format(int(pair)) for pair in pairs]
    length2 = max(len(pair) for pair in pairs)

    # Left justify keys.
    keys = ["{0:<{1}}".format(key, length - length2) for key in keys]

    # Right justify pairs.
    pairs = ["{0:>{1}}".format(pair, length2) for pair in pairs]

    for key, pair in zip(keys, pairs):
        yield key, pair


# =========
# Template.
# =========
template = TemplatingEnvironment(loader=jinja2.FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Tasks", "03")))
template.set_environment(globalvars={},
                         filters={"rjustify": rjustify,
                                  "cjustify": cjustify})
T1 = template.environment.get_template("T01")

# ==========
# Constants.
# ==========
LEVEL = 1
PROMPT = " Please choose folder, press [D] to display content or press [Q] to quit: "
REGEX = re.compile("^[A-Z]$")

# ================
# Initializations.
# ================
error = 0

# ============
# Main script.
# ============
folder, level, d_pressed, q_pressed, collection, collection2 = init()
while not q_pressed:

    folders = get_folders(folder)
    if level == 1:
        folders = filter(lambda i: REGEX.match(i[0]), folders)
    folders = dict(folders)
    menu = sorted(folders)
    while not q_pressed:
        run("CLS", shell=True)
        print(T1.render(cwd=folder, menu=menu, collection1=[], collection2=[], collection3=[]))
        prompt = PROMPT
        if level <= LEVEL:
            prompt = " Please choose folder or press [Q] to quit: "
        answer = input(prompt)
        if answer.lower() == "q":
            q_pressed = True
        elif answer.lower() == "d" and level > LEVEL:
            d_pressed, q_pressed = True, True
        else:
            try:
                folder = folders[menu[int(answer) - 1]]
            except (ValueError, IndexError, KeyError):
                continue
            else:
                if not int(answer):
                    continue
                level += 1
                break

    if d_pressed:
        for dirname, dirnames, filenames in os.walk(folder):
            if not dirnames and not filenames:
                collection2.append(dirname)
            collection.extend(list(map(os.path.join, repeat(dirname), filenames)))
        collection = sorted(sorted(sorted(collection, key=os.path.basename), key=lambda i: os.path.splitext(i)[1][1:].lower()), key=os.path.dirname)
        collection1 = pprint_files(*[(file, os.path.getsize(file)) for file in collection])
        collection3 = pprint_extensions(*[(key.upper(), len(list(group))) for key, group in groupby(sorted([os.path.splitext(file)[1][1:] for file in collection]))])
        while True:
            run("CLS", shell=True)
            print(T1.render(cwd=folder, menu=[], collection1=collection1, collection2=collection2, collection3=collection3))
            input(" Press any key to continue...")
            break
        folder, level, d_pressed, q_pressed, collection, collection2 = init()

# ============
# Exit script.
# ============
run("CLS", shell=True)
sys.exit(error)
