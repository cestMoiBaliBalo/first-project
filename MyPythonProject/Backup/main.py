# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import json
import logging.config
import operator
import os
import subprocess
import sys
from functools import partial
from itertools import chain, compress
from operator import contains, eq
from os.path import exists, expandvars, join, normpath
from pathlib import Path
from typing import Any, List, Mapping, Optional, Union
from xml.etree.ElementTree import parse

import yaml

from Applications.decorators import itemgetter_
from Applications.shared import TEMP, UTF8

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_THATFILE = Path(os.path.abspath(__file__))


# ========================
# Define custom namespace.
# ========================
class GetConfig(object):

    def __init__(self, *args) -> None:
        self._config = {arg["target"]: arg["workspace"] for arg in args}

    @property
    def config(self) -> Optional[Mapping[str, str]]:
        return self._config

    @classmethod
    def get_fromjsonfile(cls, config: Union[str, Path], encoding: str = UTF8):
        with open(config, encoding=encoding) as stream:
            items = json.load(stream)
        return cls(*items)


# =============================
# Define custom parsing action.
# =============================
class GetTargets(argparse.Action):

    def __init__(self, option_strings, dest, **kwargs):
        """

        :param option_strings:
        :param dest:
        :param kwargs:
        """
        super(GetTargets, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        """

        :param parsobj:
        :param namespace:
        :param values:
        :param option_string:
        :return:
        """
        # Tous les scripts associés au workspace sont sélectionnés par défaut.
        # Les scripts n'appartenant pas au workspace sont éliminés si une liste de scripts est reçue par le programme.
        targets = filter(itemgetter_(1)(partial(eq, namespace.workspace)), namespace.config.items())  # type: Any
        if values:
            targets = filter(itemgetter_(0)(partial(contains, values)), targets)
        targets = [tuple(compress(target, [1, 0])) for target in targets]
        setattr(namespace, self.dest, list(chain(*targets)))


# ================
# Parse arguments.
# ================
parser = argparse.ArgumentParser()
parser.add_argument("workspace", choices=["documents", "miscellaneous", "music", "pictures", "videos"])
parser.add_argument("targets", nargs="*", action=GetTargets)
parser.add_argument("-f", "--full", action="store_true")
parser.add_argument("-c", "--check", action="store_true")
parser.add_argument("-t", "--test", action="store_true")

# ===========================
# Load logging configuration.
# ===========================
with open(_THATFILE.parents[1] / "Resources" / "logging.yml", encoding=UTF8) as stream:
    logging.config.dictConfig(yaml.load(stream, Loader=yaml.FullLoader))

# ==============
# Define logger.
# ==============
logger = logging.getLogger("MyPythonProject.Areca.{0}".format(str(_THATFILE.stem)))

# ========================
# Define global constants.
# ========================
ARECA = str(Path("C:/") / "Program Files" / "Areca" / "areca_cl.exe")
TABS = 4

# =====================
# Initialize variables.
# =====================
status, codes, = 100, []  # type: int, List[int]

# ===============
# Main algorithm.
# ===============
arguments = GetConfig.get_fromjsonfile(_THATFILE.parent / "backup.json")
parser.parse_args(namespace=arguments)

#    --------------------
# 1. Log input arguments.
#    --------------------

# 1.a. Targets available in JSON reference file.
logger.debug("Configured targets.")
for target, workspace in sorted(sorted(arguments.config.items(), key=itemgetter_()(int)), key=operator.itemgetter(1)):
    logger.debug("\t%s: %s.".expandtabs(TABS), target, workspace)

# 1.b. Targets given by parser.
logger.debug("Processed targets.")
if arguments.targets:
    for target in sorted(arguments.targets, key=int):
        logger.debug("\t%s.".expandtabs(TABS), target)
elif not arguments.targets:
    logger.debug("\tAny coherent target hasn\'t been given: backup can\'t be processed!".expandtabs(TABS))

#    ------------------
# 2. Process arguments.
#    ------------------
for target in arguments.targets:

    #  2.a. Get backup configuration file.
    cfgfile = join(expandvars("%_BACKUP%"), "workspace.%s" % (arguments.workspace,), "%s.bcfg" % (target,))
    logger.debug("Configuration file.")
    logger.debug('\t"%s".'.expandtabs(TABS), cfgfile)
    try:
        assert exists(cfgfile) is True
    except AssertionError:
        logger.debug('\t"%s" doesn\'t exist: backup can\'t be processed!'.expandtabs(TABS), cfgfile)
        continue

    # 2.b. Get backup location.
    root = parse(cfgfile).getroot()
    directory = normpath(root.find("medium").get("path"))
    logger.debug("Backup location.")
    logger.debug('\t"%s".'.expandtabs(TABS), directory)
    try:
        assert exists(directory) is True
    except AssertionError:
        logger.debug('\t"%s" doesn\'t exist: backup can\'t be processed!'.expandtabs(TABS), directory)
        continue

    # 2.c. Build backup command.
    command = [ARECA, "backup"]  # type: List[str]
    if arguments.full:
        command.append("-f")
    if arguments.check:
        command.append("-c")
    command.extend(["-wdir", '"{0}"'.format(str(TEMP / "tmp-Xavier")), "-config", cfgfile])
    logger.debug("Backup command.")
    logger.debug('\t%s.'.expandtabs(TABS), " ".join(command))

    #  2.d. Run backup command.
    code = 0  # type: int
    if not arguments.test:
        process = subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True)
        code = process.returncode
        if code:
            logger.debug('"%s" was returned by "areca_cl.exe". Backup failed.', code)
            codes.append(code)
            continue
        logger.info("Backup log.")
        for line in process.stdout.splitlines():
            logger.info("\t%s".expandtabs(TABS), line)
    codes.append(code)

# ===============
# Exit algorithm.
# ===============
if all(operator.eq(code, 0) for code in codes):
    status = 0
sys.exit(status)
