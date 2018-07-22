# -*- coding: utf-8 -*-
"""
Sync local CloudStation folder from MP4 local videos folder.
Run at system start.
"""
# pylint: disable=invalid-name
import fnmatch
import logging.config
import os
import sys
from shutil import move

import yaml

from Applications.shared import grouper

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))
logger = logging.getLogger("PythonProject.Tasks.04.main")

# ==================
# Functions aliases.
# ==================
expandvars, join, listdir = os.path.expandvars, os.path.join, os.listdir

# ==========
# Constants.
# ==========
SRC = join(expandvars("%USERPROFILE%"), "Videos")
DST = join(expandvars("%_CLOUDSTATION%"), "Vidéos")

# ============
# Main script.
# ============
for group in grouper(fnmatch.filter(listdir(SRC), "*.mp4"), 3):
    for video in group:
        if video:
            try:
                move(join(SRC, video), DST)
            except FileNotFoundError:
                pass
            else:
                logger.info('"%s" moved to CloudStation', video)
    break
sys.exit(0)
