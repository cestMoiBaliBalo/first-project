# -*- coding: utf-8 -*-
import argparse
import json
import logging.config
import os
import sys

import yaml

from Applications.AudioCD.shared import upload_audiofiles
from Applications.Database.AudioCD.shared import get_trackstoupload, uploadtracks
from Applications.parsers import database_parser, loglevel_parser
from Applications.shared import base85_decode

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser(parents=[database_parser, loglevel_parser], conflict_handler="resolve", argument_default=argparse.SUPPRESS)
parser.add_argument("--test", action="store_true")
arguments = parser.parse_args()

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    config = yaml.load(fp)
for logger in ["Applications.AudioCD", "Applications.Database.AudioCD"]:
    try:
        config["loggers"][logger]["level"] = arguments.loglevel
    except KeyError:
        pass
logging.config.dictConfig(config)
logger = logging.getLogger("Applications.AudioCD")

# ===============
# Main algorithm.
# ===============
uid, uploaded = [], 0
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "configuration.json"), encoding="UTF_8") as fr:
    credentials = json.load(fr)
if "cloud" in credentials:
    # Get tracks to upload to Synology Audio Station.
    files = dict([(file, rowid) for rowid, file, utc_created in get_trackstoupload(db=arguments.db)])

    # Upload tracks then get respective ROWID.
    uid = [files[file] for file in
           upload_audiofiles(credentials["cloud"]["server"], credentials["cloud"]["user"], base85_decode(credentials["cloud"]["password"]), *list(sorted(files)), test=getattr(arguments, "test", False))]
    logger.debug(len(uid))

    # Update tracks status.
    uploaded = uploadtracks(*uid, db=arguments.db)
    logger.debug(uploaded)

sys.exit(len(uid))
