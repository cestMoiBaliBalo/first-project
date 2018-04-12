# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import logging.config
import os
import sys
from operator import itemgetter
from subprocess import run

import jinja2
import yaml

import shared
from Applications.Database.AudioCD.shared import deletelog, selectlogs_fromuid
from Applications.shared import ACCEPTEDANSWERS, TemplatingEnvironment, grouper, rjustify

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# ==========
# Functions.
# ==========
def init():
    return 0, 1, 1, False, False


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))

# ================
# Initializations.
# ================
uid = []

# =========
# Template.
# =========
template = TemplatingEnvironment(loader=jinja2.FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Tasks", "05")))
template.set_environment(globalvars={},
                         filters={"rjustify": rjustify})
T1 = template.environment.get_template("T01")

# ===============
# Main algorithm.
# ===============
level, page, step, q_pressed, delete = init()
while not q_pressed:

    if step == 1:
        database = shared.prompt_databases(T1)
        if not database:
            level, q_pressed = 100, True
        if not q_pressed:
            step += 1

    elif step == 2:
        if not database:
            run("CLS", shell=True)
            print(T1.render(menu=[], logs=[], title=""))
            input(" Some issue occurred: database not found. Press any key to quit.")
            level, q_pressed = 101, True
        if not q_pressed:
            logs = [(artist, origyear, year, album, label, genre, upc, disc, tracks, artistsort, albumsort, rowid) for
                    rowid, ripped, artistsort, albumsort, artist, origyear, year, album, label, genre, upc, application, disc, tracks, utc_created, utc_modified in selectlogs_fromuid(db=database)]
            logs = sorted(sorted(sorted(logs, key=itemgetter(3)), key=itemgetter(10)), key=itemgetter(9))
            uid = shared.prompt_logs(T1, *grouper(logs, 30))
            if not uid:
                level, q_pressed = 100, True
            if not q_pressed:
                step += 1

    elif step == 3:
        while True:
            run("CLS", shell=True)
            print(T1.render(menu=[], logs=[], title=""))
            answer = input(" Please confirm logs removal. Press [Y] to confirm or [N] to cancel: ")
            if answer.upper() not in ACCEPTEDANSWERS:
                continue
            if answer.upper() == "N":
                level = 100
            elif answer.upper() == "Y":
                delete = True
            q_pressed = True
            break

# =====================
# Remove selected logs.
# =====================
if delete:
    run("CLS", shell=True)
    print(T1.render(menu=[], logs=[], title=""))
    input(" {0:>2d} logs removed. Press any key to quit.".format(deletelog(*uid, db=database)))

# ===============
# Exit algorithm.
# ===============
run("CLS", shell=True)
sys.exit(level)
