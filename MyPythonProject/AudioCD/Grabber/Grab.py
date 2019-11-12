# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import locale
import logging.config
import os
import sys
from contextlib import suppress
from functools import partial
from operator import contains, not_

import yaml

from Applications.AudioCD.shared import AudioGenres, AudioLanguages, upsert_audiotags
from Applications.parsers import tags_grabber
from Applications.shared import UTF8, get_dirname, itemgetter_, mainscript, nested_

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


class CustomAudioGenres(AudioGenres):
    _genres = {"Arcade Fire": "Alternative Rock",
               "Black Sabbath": "Hard Rock",
               "Blue \u00D6yster Cult": "Hard Rock",
               "Bon Jovi": "Hard Rock",
               "Calogero": "French Pop",
               "Cradle of Filth": "Black Metal",
               "Deep Purple": "Hard Rock",
               "Firehouse": "Hard Rock",
               "Green Day": "Alternative Rock",
               "Indochine": "French Pop",
               "Iron Maiden": "Heavy Metal",
               "Jethro Tull": "Progressive Rock",
               "Judas Priest": "Heavy Metal",
               "King Diamond": "Hard Rock",
               "Kiss": "Hard Rock",
               "Grande Sophie, La": "French Pop",
               "Lady Gaga": "Pop",
               "Megadeth": "Trash Metal",
               "Metallica": "Trash Metal",
               "Myl\u00E8ne Farmer": "French Pop",
               "Nirvana": "Alternative Rock",
               "Ozzy Osbourne": "Hard Rock",
               "Paradise Lost": "Doom Metal",
               "Pearl Jam": "Alternative Rock",
               "Sandra": "Pop",
               "Tears for Fears": "Pop",
               "W.A.S.P.": "Hard Rock",
               "WASP": "Hard Rock",
               "Warrior Soul": "Hard Rock"}


class CustomAudioLanguages(AudioLanguages):
    _genres = {"Calogero": "French",
               "Indochine": "French",
               "Grande Sophie, La": "French",
               "Myl\u00E8ne Farmer": "French"}


# Define French environment.
locale.setlocale(locale.LC_ALL, "")

# Define local constants.
LOGGERS = ["Applications.AudioCD", "MyPythonProject"]

# Define functions aliases.
abspath, basename, join, expandvars, splitext = os.path.abspath, os.path.basename, os.path.join, os.path.expandvars, os.path.splitext

# Parse arguments.
arguments = vars(tags_grabber.parse_args())

# Get audio tags processing profile.
with open(join(get_dirname(os.path.abspath(__file__), level=2), "Resources", "profiles.yml"), encoding=UTF8) as stream:
    tags_config = yaml.load(stream, Loader=yaml.FullLoader)[arguments.get("tags_processing", "default")]

# Configure logging.
if tags_config.get("debug", False):
    with open(join(get_dirname(os.path.abspath(__file__), level=3), "Resources", "logging.yml"), encoding=UTF8) as stream:
        log_config = yaml.load(stream, Loader=yaml.FullLoader)

    for item in LOGGERS:
        with suppress(KeyError):
            log_config["loggers"][item]["level"] = "DEBUG"

    logging.config.dictConfig(log_config)
    logger = logging.getLogger("MyPythonProject.AudioCD.Grabber.{0}".format(splitext(basename(abspath(__file__)))[0]))
    logger.debug(mainscript(__file__))

# Process tags from input file.
value, _ = upsert_audiotags(arguments["profile"],
                            arguments["source"],
                            arguments["sequence"],
                            *arguments.get("decorators", ()),
                            genres=CustomAudioGenres(),
                            languages=CustomAudioLanguages(),
                            **dict(filter(nested_(not_)(itemgetter_()(partial(contains, ["debug", "console"]))), tags_config.items())))
sys.exit(value)
