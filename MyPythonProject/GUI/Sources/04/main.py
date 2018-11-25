# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import json
import locale
import logging.config
import os
from contextlib import ExitStack, suppress
from typing import List

import wx  # type: ignore
import yaml

from Applications.AudioCD.shared import upsert_audiotags
from Applications.Tables.Albums.shared import insert_albums_fromjson
from Applications.interfaces import Interface04
from Applications.shared import UTF16, UTF8, get_dirname

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, ("french", "fr_FR.ISO8859-1"))

# =================
# Global constants.
# =================
LOGGERS = ["Applications.shared", "Applications.AudioCD", "MyPythonProject"]
TXTTAGS = os.path.join(os.path.expandvars("%TEMP%"), "tags.txt")
JSONTAGS = os.path.join(os.path.expandvars("%TEMP%"), "tags.json")

# ========
# Logging.
# ========
with open(os.path.join(get_dirname(os.path.abspath(__file__), level=4), "Resources", "logging.yml"), encoding=UTF8) as fp:
    config = yaml.load(fp)

# ============
# Main script.
# ============
app = wx.App()
interface = Interface04(None)
interface.Show()
app.MainLoop()
if interface.run_clicked:

    returns = []  # type: List[int]

    # Configure logging.
    if interface.debug:
        for item in LOGGERS:
            with suppress(KeyError):
                config["loggers"][item]["level"] = "DEBUG"

        if interface.console:

            # Set up a specific stream handler.
            for item in LOGGERS:
                with suppress(KeyError):
                    config["loggers"][item]["handlers"] = ["file", "console"]
            with suppress(KeyError):
                config["handlers"]["console"]["level"] = "DEBUG"

            # Set up a specific filter for logging from "Applications.AudioCD.shared" only.
            localfilter, audiocd_filter = {}, {"class": "logging.Filter", "name": "Applications.AudioCD.shared"}
            localfilter["localfilter"] = audiocd_filter
            config["filters"] = localfilter
            config["handlers"]["console"]["filters"] = ["localfilter"]

    # Dump logging configuration.
    with open(os.path.join(os.path.expandvars("%TEMP%"), "logging.yml"), mode="w", encoding=UTF8) as stream:
        yaml.dump(config, stream, indent=2, default_flow_style=False)

    # -----
    logging.config.dictConfig(config)
    logger = logging.getLogger("MyPythonProject.AudioCD.Grabber.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

    # -----
    with open(interface.audiotags, encoding=UTF8) as stream:
        for tags in json.load(stream):

            # ----- Create an UTF-16-LE encoded plain text file displaying tags as key/value pairs.
            with open(TXTTAGS, mode="w", encoding=UTF16) as fw:
                for k, v in tags.items():
                    fw.write("{0}={1}\n".format(k.lower(), v))

            # ----- Create an "AudioCDTags object" gathering together audio tags.
            #       Create an UTF-8 encoded JSON file for database insertions if required.
            with open(TXTTAGS, mode="r+", encoding=UTF16) as fr:
                returned = upsert_audiotags(interface.profile,
                                            fr,
                                            db=interface.database,
                                            db_albums=interface.albums,
                                            db_bootlegs=interface.bootlegs,
                                            store_tags=False,
                                            drive_tags=None)  # type: int
                logger.debug(returned)
                returns.append(returned)

        # Insert tags into database if required.
        if interface.insert:
            if not any(returns):
                stack = ExitStack()
                try:
                    fr = stack.enter_context(open(JSONTAGS, encoding=UTF8))
                except FileNotFoundError as exception:
                    logger.exception(exception)
                else:
                    with stack:
                        logger.debug(insert_albums_fromjson(fr))
