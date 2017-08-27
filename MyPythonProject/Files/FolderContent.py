# -*- coding: utf-8 -*-
import os
import sys
import yaml
import json
import logging
import argparse
from logging.config import dictConfig
from Applications.parsers import foldercontent
from Applications.descriptors import Answers, Folder, Extensions
from Applications.shared import interface, filesinfolder, GlobalInterface, UTF8, WRITE

__author__ = "Xavier ROSSET"


# ========
# Classes.
# ========
class LocalInterface(GlobalInterface):

    # Data descriptor(s).
    folder = Folder()
    extensions = Extensions()
    json_output = Answers("N", "Y", default="Y")

    # Instance method(s).
    def __init__(self, *args):
        super(LocalInterface, self).__init__(*args)
        self._json_name = None

    # Properties.
    @property
    def json_name(self):
        return self._json_name

    @json_name.setter
    def json_name(self, value):
        if not value:
            value = os.path.join(os.path.expandvars("%TEMP%"), "content.json")
        if not os.path.exists(os.path.dirname(value)):
            raise ValueError('"{0}" doesn\'t exist. Please enter an existing directory'.format(os.path.dirname(value)))
        self._json_name = value


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    # --> Logging interface.
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        dictConfig(yaml.load(fp))
    logger = logging.getLogger("Default.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

    # --> Initializations.
    arguments = []

    # --> User interface.
    gui = interface(LocalInterface([("Please enter folder", "folder"), ("Please enter extension(s)", "extensions"), ("Would you like to display content in a JSON file [Y/N]?", "json_output")],
                                   {"Y": [("Please enter JSON file name", "json_name")]}
                                   )
                    )

    # --> Define new argument.
    foldercontent.add_argument("--json", dest="output", default=os.path.join(os.path.expandvars("%TEMP%"), "content.txt"), type=argparse.FileType(mode=WRITE, encoding=UTF8))

    # --> Parse arguments.
    arguments.append(gui.folder)
    arguments.extend(gui.extensions)
    if gui.json_output == "Y":
        arguments.append("--json")
        arguments.append(gui.json_name)
    arguments = foldercontent.parse_args(arguments)

    # --> Log arguments.
    logger.debug(arguments.folder)
    logger.debug(arguments.extensions)
    logger.debug(gui.json_output)

    # --> Main algorithm.

    # -->  1. Default JSON output.
    if gui.json_output == "Y":
        json.dump(sorted(sorted(filesinfolder(*arguments.extensions, folder=arguments.folder)), key=lambda i: os.path.splitext(i)[1][1:]), arguments.output, indent=4, ensure_ascii=False)
        sys.exit(0)

    # -->  2. Text output.
    for num, file in enumerate(sorted(sorted(filesinfolder(*arguments.extensions, folder=arguments.folder)), key=lambda i: os.path.splitext(i)[1][1:]), start=1):
        arguments.output.write("{0:>3d}. {1}\n".format(num, os.path.normpath(file)))
    sys.exit(0)
