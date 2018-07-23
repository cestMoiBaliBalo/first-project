# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import json
import logging.config
import os
import sys
from contextlib import ExitStack, suppress
from string import Template

import yaml

from Applications.AudioCD.shared import RippedDisc, albums, bootlegs
from Applications.parsers import tags_grabber
from Applications.shared import MUSIC, UTF8, mainscript

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# =================
# Global functions.
# =================
def get_tags(profile, source, *decorators, db=None, db_albums=False, db_bootlegs=False, store_tags=False, test=False):
    """

    :param profile:
    :param source:
    :param decorators:
    :param db:
    :param db_albums:
    :param db_bootlegs:
    :param store_tags:
    :param test:
    :return:
    """
    in_logger = logging.getLogger("MyPythonProject.AudioCD.Grabber.{0}.tags_grabber".format(os.path.splitext(os.path.basename(__file__))[0]))
    stack = ExitStack()
    value = 0
    in_logger.debug(profile)
    in_logger.debug(source.name)
    try:
        track = stack.enter_context(RippedDisc(profile, source, *decorators))
    except ValueError as err:
        in_logger.debug(err)
        value = 100
    else:
        with stack:

            # 1. Insert data into albums tables.
            if db_albums and db:
                in_logger.debug("Process default album.")
                albums(track.audiotrack, db=db)

            # 2. Insert data into bootlegs tables.
            if db_bootlegs and db:
                in_logger.debug("Process bootleg album.")
                bootlegs(track.audiotrack, db=db)

            # 3. Store both input and output tags into permanent files.
            if store_tags:

                collection = os.path.join(get_tagsfile(track.audiotrack), "input_tags.json")
                in_logger.debug(collection)
                if collection:
                    tags = []
                    with suppress(FileNotFoundError):
                        with open(collection, encoding=UTF8) as fr:
                            tags = json.load(fr)
                    tags.append(dict(track.intags))
                    with ExitStack() as stack:
                        json_stream = stack.enter_context(open(collection, mode="w", encoding=UTF8))
                        yaml_stream = stack.enter_context(open("{0}.yml".format(os.path.splitext(collection)[0]), mode="w", encoding=UTF8))
                        json.dump(tags, json_stream, indent=4, ensure_ascii=False, sort_keys=True)
                        yaml.dump(tags, yaml_stream, default_flow_style=False, indent=4)

                collection = os.path.join(get_tagsfile(track.audiotrack), "output_tags.json")
                in_logger.debug(collection)
                if collection:
                    tags = []
                    with suppress(FileNotFoundError):
                        with open(collection, encoding=UTF8) as fr:
                            tags = json.load(fr)
                    tags.append(dict(track.audiotrack))
                    with ExitStack() as stack:
                        json_stream = stack.enter_context(open(collection, mode="w", encoding=UTF8))
                        yaml_stream = stack.enter_context(open("{0}.yml".format(os.path.splitext(collection)[0]), mode="w", encoding=UTF8))
                        json.dump(tags, json_stream, indent=4, ensure_ascii=False, sort_keys=True)
                        yaml.dump(tags, yaml_stream, default_flow_style=False, indent=4)

            # 4. Store input tags into JSON test configuration.
            if test:
                mapping = {}
                collection = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Tests", "tags.json")
                with suppress(FileNotFoundError):
                    with open(collection, encoding=UTF8) as fr:
                        mapping = json.load(fr)
                if profile not in mapping:
                    mapping[profile] = dict(track.intags)
                    with open(collection, mode="w", encoding=UTF8) as fw:
                        json.dump(mapping, fw, indent=4, ensure_ascii=False, sort_keys=True)

    return value


def get_tagsfile(obj):
    """

    :param obj:
    :return:
    """
    in_logger = logging.getLogger("MyPythonProject.AudioCD.Grabber.{0}.get_tagsfile".format(os.path.splitext(os.path.basename(__file__))[0]))
    tags = {}

    # -----
    for key in ["albumsortcount",
                "foldersortcount",
                "artistsort_letter",
                "artistsort",
                "origyear",
                "album",
                "discnumber",
                "bootlegalbumyear",
                "bootlegalbummonth",
                "bootlegalbumday",
                "bootlegalbumcity",
                "bootlegalbumcountry"]:
        with suppress(AttributeError):
            tags[key] = getattr(obj, key)
    in_logger.debug(tags)

    # -----
    with open(os.path.join(os.path.expandvars("%_RESOURCES%"), "tags.yml"), encoding=UTF8) as stream:
        templates = yaml.load(stream)
    in_logger.debug(templates)

    # Load templates respective to "bootleg" value.
    template = templates.get(obj.bootleg, templates["N"])

    # Load templates respective to "artistsort" value.
    template = template.get(obj.artistsort, template["default"])

    # Load templates respective to "foldersortcount" value.
    template = template.get(obj.foldersortcount, template["N"])

    # Load template respective to "totaldiscs" value.
    template = template.get(str(obj.totaldiscs), template["9"])

    # Return tags file dirname.
    return Template(os.path.join(MUSIC, template)).substitute(tags)


# ============
# Main script.
# ============
if __name__ == "__main__":

    # Local constants.
    LOGGERS = ["Applications.AudioCD", "MyPythonProject"]
    MAPPING = {True: "debug", False: "info"}

    # Functions aliases.
    basename, join, expandvars, splitext = os.path.basename, os.path.join, os.path.expandvars, os.path.splitext

    # Parse arguments.
    arguments = vars(tags_grabber.parse_args())

    # Get arguments.

    # ----- Debug mode.
    l_debug = arguments.get("debug", False)

    # ----- Output database.
    l_database = arguments.get("db")

    # ----- Decorators.
    l_decorators = arguments.get("decorators", ())

    # ----- Store both input and output tags?
    l_store_tags = arguments.get("store_tags", False)

    # ----- Store tags sample?
    l_test = arguments.get("test", False)

    # Configure logging.
    with open(join(expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
        config = yaml.load(fp)
    for logger in LOGGERS:
        with suppress(KeyError):
            config["loggers"][logger]["level"] = MAPPING[l_debug].upper()
    logging.config.dictConfig(config)
    logger = logging.getLogger("MyPythonProject.AudioCD.Grabber.{0}".format(splitext(basename(__file__))[0]))

    # Grab tags from input file.
    logger.debug(mainscript(__file__))
    sys.exit(
            get_tags(arguments.get("profile"), arguments.get("source"), *l_decorators, db=l_database, db_albums=arguments.get("albums"), db_bootlegs=arguments.get("bootlegs"), store_tags=l_store_tags,
                     test=l_test))
