# -*- coding: utf-8 -*-
"""
Sync mobile devices from local audio repositories.
Called from tasks manager "tasks.cmd". Option "32".
"""
# pylint: disable=invalid-name
import argparse
import json
import logging.config
import os
import re
import sys
from subprocess import PIPE, run

import jinja2
import yaml

from Applications.shared import ACCEPTEDANSWERS, TemplatingEnvironment, rjustify

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))

# ================
# Argument parser.
# ================
parser = argparse.ArgumentParser()
parser.add_argument("outfile",
                    type=argparse.FileType("w", encoding="ISO-8859-1"),
                    nargs="?",
                    default=os.path.join(os.path.expandvars("%TEMP%"), "xxcopy.cmd"),
                    help="DOS commands file running XXCOPY statements.")
arguments = parser.parse_args()

# ====================
# Regular expressions.
# ====================
REGEX = re.compile(r"^[I-R]:$")

# =========
# Template.
# =========
template = TemplatingEnvironment(loader=jinja2.FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Tasks", "02")))
template.set_environment(globalvars={},
                         filters={"rjustify": rjustify})
T1 = template.environment.get_template("T01")
T2 = template.environment.get_template("T02")

# ================
# Initializations.
# ================
extra_patterns, command1, command2, compression, copy, level, patterns, step, q_pressed = [], [], [], "", False, 0, [], 1, False

# =========================
# Load audio configuration.
# =========================
with open(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Tasks", "Resources", "Configuration.json")) as fr:
    configuration = json.load(fr)
repositories = sorted(configuration.get("repositories"))

# ============
# Main script.
# ============
while not q_pressed:

    #    °°°°°°°°°°°°°°°°°°°°°°°°°
    # A. Choose source repository.
    #    °°°°°°°°°°°°°°°°°°°°°°°°°
    if step == 1:
        while True:
            run("CLS", shell=True)
            print(T1.render(menu=repositories, title="Available audio repositories:"))
            answer = input(" Please choose source repository or press [Q] to quit: ")
            if answer.upper() == "Q":
                q_pressed = True
                level = 100
                break
            try:
                repository = repositories[int(answer) - 1]
            except (ValueError, IndexError):
                continue
            else:
                if not int(answer):
                    continue
                repository = configuration["repositories"][repository]
                compression = configuration["compression"][repository]
                patterns = configuration["patterns"][compression]
                extra_patterns = configuration["extra_patterns"].get(compression)
                step += 1
                break
        if compression.upper() == "LOSSLESS":
            step += 1

    # °°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    # B. Add extra files if lossy repository has been chosen.
    #    °°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°
    elif step == 2:
        while True:
            run("CLS", shell=True)
            print(T1.render(menu=[]))
            answer = input(" Would you like to insert MPEG-4 audio files too? Press [Y] for Yes or [N] for No. ")
            if answer.upper() not in ACCEPTEDANSWERS:
                continue
            if answer.upper() == "Y":
                patterns.extend(extra_patterns)
            step += 1
            break

    # °°°°°°°°°°°°°°°°°°°°°°°°°
    # C. Choose destination drive.
    #    °°°°°°°°°°°°°°°°°°°°°°°°°
    elif step == 3:
        process = run("wmic logicaldisk get name", shell=True, universal_newlines=True, stdout=PIPE)
        drives = [drive.rstrip() for drive in process.stdout.splitlines() if REGEX.match(drive.rstrip())]
        if not drives:
            run("CLS", shell=True)
            print(T1.render(menu=[]))
            input(" No destination drive found. Press any key to quit.")
            q_pressed = True
            level = 101
        if not q_pressed:
            while True:
                run("CLS", shell=True)
                print(T1.render(menu=drives, title="Available drives:"))
                answer = input(" Please choose destination drive or press [Q] to quit: ")
                if answer.upper() == "Q":
                    q_pressed = True
                    level = 100
                    break
                try:
                    drive = drives[int(answer) - 1]
                except (ValueError, IndexError):
                    continue
                else:
                    if not int(answer):
                        continue
                    step += 1
                    break

    # °°°°°°°°°°°°°°°°°°°°
    # D. Sync another device.
    #    °°°°°°°°°°°°°°°°°°°°
    elif step == 4:
        if not repository or not drive:
            run("CLS", shell=True)
            print(T1.render(menu=[]))
            input(" Some issue occurred: source repository or destination drive is missing. Press any key to quit.")
            q_pressed = True
            level = 102
        if not q_pressed:
            command1.extend([(repository, pattern, drive) for pattern in patterns])
            command2.append((drive, repository))
            while True:
                run("CLS", shell=True)
                print(T1.render(menu=[]))
                answer = input(" Would you like to sync another device? Press [Y] for Yes or [N] for No. ")
                if answer.upper() not in ACCEPTEDANSWERS:
                    continue
                if answer.upper() == "N":
                    step += 1
                elif answer.upper() == "Y":
                    step = 1
                break

    # °°°°°°°°°°°°°°°
    # E. Confirm copies.
    #    °°°°°°°°°°°°°°°
    elif step == 5:
        while True:
            run("CLS", shell=True)
            print(T1.render(menu=[]))
            answer = input(" Would you like to sync the chosen device(s)? Press [Y] for Yes or [N] for No. ")
            if answer.upper() not in ACCEPTEDANSWERS:
                continue
            if answer.upper() == "N":
                level = 1
            q_pressed = True
            copy = True
            break

# =========================
# Create DOS commands file.
# =========================
if copy:
    arguments.outfile.write(T2.render(command1=command1, command2=command2))

# ============
# Exit script.
# ============
run("CLS", shell=True)
sys.exit(level)
