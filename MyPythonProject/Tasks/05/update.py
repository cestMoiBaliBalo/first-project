# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import logging.config
import os
import sys
from collections import OrderedDict
from itertools import chain, repeat
from operator import itemgetter
from subprocess import run

import jinja2
import yaml

import shared
from Applications.Tables.RippedDiscs.shared import deletelog, selectlogs_fromuid
from Applications.shared import LOCAL, TemplatingEnvironment, UTC, format_date, grouper, rjustify

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

# ==========
# Constants.
# ==========
EXTRACTED_TAGS = ("ROWID", "Artistsort", "Albumsort", "Artist", "Origyear", "Year", "Album", "Label", "Genre", "UPC", "Disc", "Tracks", "Ripped", "Created", "Modified")
ALTERABLE_TAGS = ("Artistsort", "Albumsort", "Artist", "Origyear", "Year", "Album", "Label", "Genre", "UPC", "Disc", "Tracks", "Ripped")

# ================
# Initializations.
# ================
menu, uid, tags_dict = [], [], {}

# =========
# Template.
# =========
template = TemplatingEnvironment(loader=jinja2.FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Tasks", "05")))
template.set_environment(globalvars={},
                         filters={"rjustify": rjustify})
T1 = template.environment.get_template("T01")
T2 = template.environment.get_template("T02")

# ===============
# Main algorithm.
# ===============
error, page, step, q_pressed, update = init()
while not q_pressed:

    if step == 1:
        database = shared.prompt_databases(T1)
        if not database:
            error, q_pressed = 100, True
        if not q_pressed:
            step += 1

    elif step == 2:
        if not database:
            run("CLS", shell=True)
            print(T1.render(menu=[], logs=[], title=""))
            input(" Some issue occurred: database not found. Press any key to quit.")
            error, q_pressed = 101, True
        if not q_pressed:
            logs = [(artist, origyear, year, album, label, genre, upc, disc, tracks, artistsort, albumsort, rowid) for
                    rowid, ripped, artistsort, albumsort, artist, origyear, year, album, label, genre, upc, application, disc, tracks, utc_created, utc_modified in selectlogs_fromuid(db=database)]
            logs = sorted(sorted(sorted(logs, key=itemgetter(3)), key=itemgetter(10)), key=itemgetter(9))
            uid = shared.prompt_logs(T1, *grouper(logs, 30))
            if not uid:
                error, q_pressed = 100, True
            if not q_pressed:
                step += 1
                log = list(selectlogs_fromuid(*uid, db=database))
                if log:
                    if len(log) == 1:
                        # Headers.
                        tags = list(EXTRACTED_TAGS)
                        max_length_tag = max(map(len, tags))

                        # Selected log.
                        values = [(rowid,
                                   artistsort,
                                   albumsort,
                                   artist,
                                   origyear,
                                   year,
                                   album,
                                   label,
                                   genre,
                                   upc,
                                   disc,
                                   tracks,
                                   format_date(UTC.localize(ripped).astimezone(LOCAL)),
                                   format_date(UTC.localize(utc_created).astimezone(LOCAL))) for
                                  rowid, ripped, artistsort, albumsort, artist, origyear, year, album, label, genre, upc, application, disc, tracks, utc_created, utc_modified in log]
                        values = list(chain.from_iterable(values))
                        max_length_value = max(map(len, map(str, values)))

                        # Pretty print both tags and values.
                        tags = ["{0:<{1}}".format(tag, max_length_tag) for tag in tags]
                        values = ["{0:<{1}}".format(str(value), max_length_value + 25) for value in values]

                        # Set dictionary with structure {tag: (tag, actual value, new value)}.
                        tags_dict = OrderedDict(zip([tag.lower() for tag in EXTRACTED_TAGS], [(tag, cur_value, new_value) for tag, cur_value, new_value in zip(tags, values, repeat(None))]))

                        # Initialize alterable tags menu.
                        menu = list(ALTERABLE_TAGS)

    elif step == 3:
        if not tags_dict:
            run("CLS", shell=True)
            print(T1.render(menu=[], logs=[], title=""))
            input(" Some issue occurred: no tags found for the selected log. Press any key to quit.")
            error, q_pressed = 102, True
        if not q_pressed:
            while True:
                run("CLS", shell=True)
                print(T2.render(log=tags_dict, menu=menu, title="Available alterable tags: "))
                prompt = " Please choose the tag to alter or press [Q] to quit: "
                promptU = list(filter(None, [value[2] for tag, value in tags_dict.items()]))
                if promptU:
                    prompt = " Please choose the tag to alter, press [A] to alter the log or press [Q] to quit: "
                answer = input(prompt)
                if answer.upper() == "A":
                    update, q_pressed = True, True
                    break
                if answer.upper() == "Q":
                    error, q_pressed = 100, True
                    break
                try:
                    tag = menu[int(answer) - 1]
                except (ValueError, IndexError):
                    continue
                else:
                    if not int(answer):
                        continue
                step += 1
                break

    elif step == 4:
        if not tag:
            run("CLS", shell=True)
            print(T1.render(menu=[], logs=[], title=""))
            input(" Some issue occurred: tag name not found. Press any key to quit.")
            error, q_pressed = 103, True
        if not q_pressed:
            while True:
                run("CLS", shell=True)
                print(T2.render(log=tags_dict, menu=[], title=""))
                answer = input(" Please enter '{0}' new value or press [Q] to quit: ".format(tag))
                if answer.upper() == "B":
                    step = 3
                    break
                if answer.upper() == "Q":
                    error, q_pressed = 100, True
                    break
                try:
                    tags_dict[tag.lower()] = tags_dict[tag.lower()][0], tags_dict[tag.lower()][1], answer
                except KeyError:
                    pass
                finally:
                    menu.remove(tag)
                    step = 3
                    break

# =====================
# Remove selected logs.
# =====================
if update:
    run("CLS", shell=True)
    print(T1.render(menu=[], logs=[], title=""))
    input(" {0:>2d} logs removed. Press any key to quit.".format(deletelog(*uid, db=database)))

# ===============
# Exit algorithm.
# ===============
run("CLS", shell=True)
sys.exit(error)
