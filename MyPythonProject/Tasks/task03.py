# -*- coding: utf-8 -*-
import argparse
import functools
import logging
import os
import sys
from logging.config import dictConfig

import yaml

from Applications.Database.DigitalAudioFiles.shared import checkalbumid, getplayedcount, updatealbum
from Applications.Database.Tables.shared import isdeltareached, update
from Applications.parsers import database_parser

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"


# ===========
# Decorators.
# ===========
def deco1(func):
    def wrapper(db, t):
        return func(t[1], db=db)

    return wrapper


def deco2(func):
    def wrapper(db, albumid):
        return func(albumid, db=db)

    return wrapper


def deco3(func):
    def wrapper(db, *args):
        changes = 0
        for date, count, rowid in args:
            changes += func(rowid, db=db, played=date, count=count)
        return changes

    return wrapper


# ===============
# Main algorithm.
# ===============

# 1. --> Define argument to force ZIP file creation.
parser = argparse.ArgumentParser(parents=[database_parser])
parser.add_argument("-f", "--forced", action="store_true")

# 2. --> Logging.
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Applications.shared.zipfiles")

# 3 --> Decorator(s).
checkalbumid = deco1(checkalbumid)
getcount = deco2(getplayedcount)
updatealbum = deco3(updatealbum)

# 4. --> Constant(s).
UID = 1234567800

#  4. --> Initialization(s).
status, arguments = 0, parser.parse_args()
isdeltareached, update, checkalbumid, getcount, updatealbum = functools.partial(isdeltareached, UID, "tasks"), \
                                                              functools.partial(update, UID, "tasks"), \
                                                              functools.partial(checkalbumid, arguments.db), functools.partial(getcount, arguments.db), \
                                                              functools.partial(updatealbum, arguments.db)

#  5. --> Main algorithm.
deltareached, previous_date = isdeltareached(db=arguments.db)
if deltareached or arguments.forced:
    # XML part. Return a list of albums IDs read since `previous_date` --> `mylist`.
    # Remove from `mylist` albumid absent from `albums` table.
    mylist = list(filter(checkalbumid, mylist))
    # Append played count.
    mylist = ((date, count + 1, rowid) for (albumid, date), (count, rowid) in zip(mylist, map(deco2, (item[0] for item in mylist))) if rowid is not None)
    # SQL part. Update `albums`.
    changes = updatealbum(*mylist)
    logger.debug(changes)
    # SQL part. Update `tasks`.
    changes = update(db=arguments.db)
    logger.debug(changes)

# 6. --> Exit algorithm.
logger.info(status)
sys.exit(status)
