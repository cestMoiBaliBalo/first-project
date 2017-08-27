# -*- coding: utf-8 -*-
import os
import yaml
import logging
import argparse
import Applications.xml
from os.path import normpath
import xml.etree.ElementTree as ET
from logging.config import dictConfig
from Applications.AudioCD.shared import AudioFilesList
from Applications.descriptors import Folder, Extensions
from Applications.shared import validpath, xsltransform, interface, GlobalInterface

__author__ = 'Xavier ROSSET'


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF-8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Applications.AudioCD.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))


# ==========
# Constants.
# ==========
XML = os.path.join(os.path.expandvars("%TEMP%"), "DigitalAudioFiles.xml")
XSL = os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Files", "DigitalAudioFiles.xsl")
HTML = os.path.join(os.path.expandvars("%_COMPUTING%"), "DigitalAudioFiles.html")


# ========
# Classes.
# ========
class LocalInterface(GlobalInterface):

    # Data descriptors.
    folder = Folder()
    extensions = Extensions()

    # Instance methods.
    def __init__(self, *args):
        super(LocalInterface, self).__init__(*args)


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("directory", help="mandatory directory to walk through", type=validpath)
parser.add_argument("extensions", help="one or more extension(s) to filter out", nargs="*")


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    # -->  1. Initializations.
    arguments = []

    # -->  2. User interface.
    gui = interface(LocalInterface([("Please enter directory to walk through", "folder"), ("Please enter extension(s) to filter out", "extensions")]))

    # -->  3. Parse arguments.
    arguments.append(gui.folder)
    arguments.extend(gui.extensions)
    arguments = parser.parse_args(arguments)

    # -->  4. Build XML file.
    ET.ElementTree(Applications.xml.audiofileslist(AudioFilesList(*arguments.extensions, folder=normpath(arguments.directory), excluded=["recycle", "\$recycle"]))).write(XML, encoding="UTF-8", xml_declaration=True)

    # -->  5. Build HTML file.
    if os.path.exists(XML):
        logger.debug(xsltransform(XML, XSL, HTML))
