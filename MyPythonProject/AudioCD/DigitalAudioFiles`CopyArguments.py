# -*- coding: utf-8 -*-
"""
Stocker dans un fichier JSON les arguments permettant de copier un fichier audio FLAC reçu en qualité de premier paramètre.
La lettre identifiant le lecteur reçevant le fichier copié est reçue en qualité de deuxième paramètre.
Le nom du fichier JSON est reçu en qualité de troisième paramètre.
Le répertoire et le nom du fichier copié sont fonction des metadata "albumsort", "disc", "track" et "title".
"""
from Applications.AudioCD.shared import getmetadata
from Applications.shared import mainscript
from logging.config import dictConfig
import argparse
import logging
import yaml
import json
import sys
import os
import re

__author__ = 'Xavier ROSSET'


# ==========
# Functions.
# ==========
def validfile(f):
    if not os.path.exists(f):
        raise argparse.ArgumentTypeError('"{0}" isn\'t a valid file.'.format(f))
    return f


def validdrive(d):
    if not os.path.exists(d):
        raise argparse.ArgumentTypeError('"{0}" isn\'t a valid drive.'.format(d))
    return d


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("file", type=validfile)
parser.add_argument("drive", type=validdrive)
parser.add_argument("-o", "--out", dest="outjsonfile", default=os.path.join(os.path.expandvars("%TEMP%"), "arguments.json"))


# =========
# Contants.
# =========
TABSIZE = 3


# ================
# Initializations.
# ================
status, args, arguments = 100, [], parser.parse_args()


# ====================
# Regular expressions.
# ====================
rex1 = re.compile(r"((?:[^\\]+\\){3})", re.IGNORECASE)
rex2 = re.compile(r"[a-z]:", re.IGNORECASE)


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Applications.AudioCD.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))


# ===============
# Main algorithm.
# ===============

#  1. Get metadata from input file.
metadata = getmetadata(arguments.file)

#  2. Process metadata.
if metadata.found:
    disc = metadata.tags.get("disc") or metadata.tags.get("discnumber")
    track = metadata.tags.get("track") or metadata.tags.get("tracknumber")
    logger.debug("Tags.")
    logger.debug("\tAlbumSort: {0}".format(metadata.tags["albumsort"][:-3]).expandtabs(TABSIZE))
    logger.debug("\tDisc     : {0}".format(disc).expandtabs(TABSIZE))
    logger.debug("\tTrack    : {0}".format(track).expandtabs(TABSIZE))
    logger.debug("\tTitle    : {0}".format(metadata.tags["title"]).expandtabs(TABSIZE))
    if os.path.exists(arguments.outjsonfile):
        with open(arguments.outjsonfile, encoding="UTF_8") as fp:
            args = json.load(fp)
    match = rex1.match(arguments.file)
    if match:
        dst = os.path.normpath(os.path.join(rex2.sub(arguments.drive, match.group(1)), metadata.tags["albumsort"][:-3], "{0}.{1}.{2}{3}".format(disc,
                                                                                                                                                track.zfill(2),
                                                                                                                                                metadata.tags["title"],
                                                                                                                                                os.path.splitext(arguments.file)[1]
                                                                                                                                                )
                                            )
                               )
        args.extend([(arguments.file, dst)])
    if args:
        with open(arguments.outjsonfile, mode="w", encoding="UTF_8") as fp:
            json.dump(args, fp, indent=4)
            status = 0
            logger.debug("Copy arguments written.")

sys.exit(status)
