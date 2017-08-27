# -*- coding: utf-8 -*-
from Applications.Database.DigitalAudioFiles.shared import deletefromuid
from logging.config import dictConfig
import argparse
import logging
import yaml
import os

__author__ = 'Xavier ROSSET'


parser = argparse.ArgumentParser()
parser.add_argument("uid", nargs="+")
argument = parser.parse_args()

with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Applications.Database.DigitalAudioFiles.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

for album, disc, track in map(deletefromuid, argument.uid):
    logger.info(album)
    logger.info(disc)
    logger.info(track)

