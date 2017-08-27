# -*- coding: utf-8 -*-
import os
import json
import yaml
import logging
from logging.config import dictConfig
from Applications.descriptors import File
from Applications.shared import UTF8, GlobalInterface, interface
from Applications.AudioCD.shared import copy_audiofiles_to_remotedirectory

__author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
class LocalInterface(GlobalInterface):

    # Descriptor(s).
    file = File()

    # Instance method(s).
    def __init__(self, *args):
        super(LocalInterface, self).__init__(*args)


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    # --> Logging.
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding=UTF8) as fp:
        dictConfig(yaml.load(fp))
    logger = logging.getLogger("AudioCD.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

    # --> User interface.
    gui = interface(LocalInterface(("Please enter input file", "file")))

    # --> Main algorithm.
    with open(gui.file, encoding=UTF8) as fp:
        copy_audiofiles_to_remotedirectory(*json.load(fp))
