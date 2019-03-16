# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import json
import logging.config
import operator
import os
import subprocess
import sys
from os.path import exists, expandvars, join, normpath
from pathlib import PureWindowsPath
from typing import List, Mapping
from xml.etree.ElementTree import parse

import yaml

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ===============
# Backup targets.
# ===============
with open(PureWindowsPath(expandvars("%_PYTHONPROJECT%")) / "Areca" / "Areca.json", encoding="UTF_8") as fp:
    targets = {item["target"]: item["workspace"] for item in json.load(fp)}  # type: Mapping[str, str]


# ========
# Classes.
# ========
class GetTargets(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super(GetTargets, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        # Tous les scripts associés au workspace sont sélectionnés par défaut.
        setattr(namespace, self.dest, list(filter(lambda i: targets[i] == getattr(namespace, "workspace"), targets.keys())))

        # Les scripts n'appartenant pas au workspace sont éliminés si une liste de scripts est reçue par le programme.
        if values:
            setattr(namespace, self.dest, list(filter(lambda i: targets[i] == getattr(namespace, "workspace"), filter(lambda i: i in targets, values))))


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("workspace", choices=["documents", "miscellaneous", "music", "pictures", "videos"])
parser.add_argument("targets", nargs="*", action=GetTargets)
parser.add_argument("-f", "--full", action="store_true")
parser.add_argument("-c", "--check", action="store_true")
parser.add_argument("-t", "--test", action="store_true")

# ========
# Logging.
# ========
with open(PureWindowsPath(expandvars("%_PYTHONPROJECT%")) / "Resources" / "logging.yml", encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))
logger = logging.getLogger("MyPythonProject.Areca.{0}".format(str(PureWindowsPath(os.path.abspath(__file__)).stem)))

# ==========
# Constants.
# ==========
ARECA = str(PureWindowsPath("C:/Program Files", "Areca", "areca_cl.exe"))
TABS = 4

# ================
# Initializations.
# ================
status, codes, = 100, []  # type: int, List[int]

# ===============
# Main algorithm.
# ===============
arguments = parser.parse_args()

#    --------------------
# 1. Log input arguments.
#    --------------------

# 1.a. Targets available in JSON reference file.
logger.debug("Configured targets.")
for target, workspace in sorted(sorted(targets.items(), key=lambda i: int(i[0])), key=operator.itemgetter(1)):
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
    command.extend(["-wdir", '"{0}"'.format(str(PureWindowsPath(expandvars("%TEMP%")) / "tmp-Xavier")), "-config", cfgfile])
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
