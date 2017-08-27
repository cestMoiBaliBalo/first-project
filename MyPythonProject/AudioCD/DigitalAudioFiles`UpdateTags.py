# -*- coding: utf-8 -*-
from Applications.AudioCD.shared import validdelay, audiofilesinfolder, updatemetadata
from Applications.shared import DFTYEARREGEX, UTF8
from logging.config import dictConfig
import argparse
import logging
import sched
import yaml
import sys
import os
import re

__author__ = 'Xavier ROSSET'


# ============
# Local names.
# ============
basename, dirname, exists, splitext = os.path.basename, os.path.dirname, os.path.exists, os.path.splitext


# ==========
# Functions.
# ==========
def validfolder(f):
    if not exists(f):
        raise argparse.ArgumentTypeError('"{0}" isn\'t a valid folder.'.format(f))
    return f


def updatetags(*args, **kwargs):

    logger = logging.getLogger("Applications.AudioCD")
    rex = re.compile(r"^(?:{0})\.\d -\B".format(DFTYEARREGEX))
    if "folder" not in kwargs:
        return False
    if "test" not in kwargs:
        return False
    l = []

    for num, (fil, audioobj, tags) in enumerate(audiofilesinfolder(*args, folder=kwargs["folder"]), start=1):
        if any(tag not in tags for tag in ["album", "albumsort", "titlesort"]):
            continue
        if rex.match(tags["album"]):
            continue
        if tags["titlesort"][-1].upper() == "Y":
            continue
        if tags["albumsort"].startswith("2."):
            continue
        album = "{0}.{1} - {2}".format(tags["albumsort"][2:6], tags["albumsort"][11], tags["album"])
        logger.debug('{0:>3d}. "{1}".'.format(num, fil))
        logger.debug("\t{0}".format(type(audioobj)).expandtabs(5))
        logger.debug('\tNew album: "{0}".'.format(album).expandtabs(5))
        if not kwargs["test"]:
            if updatemetadata(audioobj, logger=logger, album=album):
                logger.debug('\t"{0}" updated.'.format(fil).expandtabs(5))
                l.append(fil)

    if l:
        logger.debug("{0:>3d} file(s) updated.".format(len(l)))
        return True

    return False


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("folder", type=validfolder)
parser.add_argument("-d", "--delay", type=validdelay, default="0")
parser.add_argument("-t", "--test", action="store_true")


# ==========
# Constants.
# ==========
ARGS = ("FLAC", "APE")


# ================
# Initializations.
# ================
arguments = parser.parse_args()
kywargs = {"folder": arguments.folder, "test": arguments.test}


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding=UTF8) as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Applications.AudioCD.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))
logger.debug("Delay: {0} second(s).".format(arguments.delay))
logger.debug("Test : {0}.".format(arguments.test))


# ===============
# Main algorithm.
# ===============

# Mise à jour immédiate.
if not arguments.delay:
    updatetags(*ARGS, **kywargs)
    sys.exit(0)

# Mise à jour différée.
s = sched.scheduler()
s.enter(arguments.delay, 1, updatetags, argument=ARGS, kwargs=kywargs)
s.run()
