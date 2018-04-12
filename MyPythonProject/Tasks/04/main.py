# -*- coding: utf-8 -*-
import logging.config
import os
from fnmatch import fnmatch
from shutil import move
import sys

import yaml

from Applications.shared import grouper

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))
logger = logging.getLogger("TASK04")

SRC = os.path.join(os.path.expandvars("%USERPROFILE%"), "Videos")
DST = os.path.join(os.path.expandvars("%_CLOUDSTATION%"), "Vidéos")

for video in list(grouper(filter(lambda i: fnmatch(i, "*.mp4"), os.listdir(SRC)), 3))[0]:
    if video:
        try:
            move(os.path.join(SRC, video), DST)
        except FileNotFoundError:
            pass
        else:
            logger.info('"{0}" moved to CloudStation'.format(video))

sys.exit(0)
