# -*- coding: utf-8 -*-
"""
Sync local audio repositories from local audio drive.
Called from tasks manager "tasks.cmd". Option "31".
"""
# pylint: disable=invalid-name
import argparse
import itertools
import json
import logging.config
import os
import re
import sys
from collections import OrderedDict
from contextlib import ExitStack
from operator import itemgetter
from subprocess import run

import jinja2
import yaml

from Applications.shared import ACCEPTEDANSWERS, ChangeLocalCurrentDirectory, DFTDAYREGEX, DFTMONTHREGEX, DFTYEARREGEX, MUSIC, TemplatingEnvironment, rjustify

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))


# ==========
# Functions.
# ==========
def get_artists(directory=MUSIC):
    for _artist, _artist_path in itertools.chain.from_iterable([list(get_folders(letter_path)) for letter, letter_path in get_folders(directory)]):
        yield _artist, _artist_path


def get_albums(directory):
    for _name, _path in get_folders(directory):
        if _name in ["1", "2"]:
            for _album, _album_path, _albumsort in get_albums(_path):
                yield _album, _album_path, _albumsort
        else:
            match = REGEX1.match(_name)
            if match:
                album = match.group(4)
                category = "1"
                sort = match.group(3)
                year = match.group(1)
                match = REGEX2.search(_path)
                if match:
                    category = match.group(1)
                if not sort:
                    sort = "1"
                yield album, _path, "{0}.{1}0000.{2}".format(category, year, sort)
            elif not match:
                match = REGEX3.match(_name)
                if match:
                    for _album, _album_path, _albumsort in get_albums(_path):
                        yield _album, _album_path, _albumsort
                elif not match:
                    match = REGEX4.match(_name)
                    if match:
                        match = REGEX5.search(_path)
                        if match:
                            category = match.group(1)
                            day = match.group(4)
                            month = match.group(3)
                            sort = match.group(5)
                            year = match.group(2)
                            if not sort:
                                sort = "1"
                            yield _name, _path, "{0}.{1}{2}{3}.{4}".format(category, year, month, day, sort)


def get_folders(directory):
    _collection = []
    stack = ExitStack()
    try:
        stack.enter_context(ChangeLocalCurrentDirectory(directory))
    except PermissionError:
        pass
    else:
        with stack:
            _collection = [(name, os.path.join(os.getcwd(), name)) for name in os.listdir(".")]
    for name, path in _collection:
        yield name, path


def has_extension(directory, *extensions):
    mapping, ext = {False: 0, True: 1}, []
    for _, _dirnames, _filenames in os.walk(directory):
        if not _dirnames:
            if _filenames:
                ext.extend(os.path.splitext(file)[1][1:] for file in _filenames)
    return mapping[any(map(lambda i: bool(i.lower() in [extension.lower() for extension in extensions]), ext))]


def init():
    return "", "", 1


# ================
# Argument parser.
# ================
parser = argparse.ArgumentParser()
parser.add_argument("outfile",
                    type=argparse.FileType("w", encoding="ISO-8859-1"),
                    nargs="?",
                    default=os.path.join(os.path.expandvars("%TEMP%"), "xxcopy.cmd"),
                    help="DOS commands file running XXCOPY statements.")
args = parser.parse_args()

# ====================
# Regular expressions.
# ====================
REGEX1 = re.compile(r"^(?=(?:{0})(?:\.\d)?\b.+$)({0})(\.(\d))?\b\s-\s\b(.+)$".format(DFTYEARREGEX))
REGEX2 = re.compile(r"\b\\([12])\\\b(?:{0})(?:\.\d)?\b\s-\s\b(?:.+)$".format(DFTYEARREGEX))
REGEX3 = re.compile(r"^(?:{0})$".format(DFTYEARREGEX))
REGEX4 = re.compile(r"^(?:{0})\.(?:{1})(?:\.\d)?\b\s-\s\b(?:.+)$".format(DFTMONTHREGEX, DFTDAYREGEX))
REGEX5 = re.compile(r"\b\\([12])\\({0})\\\b({1})\.({2})(?:\.(\d))?\b\s-\s\b(?:.+)$".format(DFTYEARREGEX, DFTMONTHREGEX, DFTDAYREGEX))

# =========================
# Load audio configuration.
# =========================
with open(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Tasks", "Resources", "Configuration.json")) as fr:
    configuration = json.load(fr)

# ==========
# Templates.
# ==========
template = TemplatingEnvironment(loader=jinja2.FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Tasks", "01")))
template.set_environment(globalvars={},
                         filters={"rjustify": rjustify})
T1 = template.environment.get_template("T01")
T2 = template.environment.get_template("T02")

# ================
# Initializations.
# ================
repositories = sorted(configuration.get("repositories"))
arguments, collection, extensions = [], [], []
copy, q_pressed = False, False
level = 0

# ============
# Main script.
# ============
source, destination, step = init()
while not q_pressed:

    #    -------------------
    # A. Pick up repository.
    #    -------------------
    if step == 1:
        while True:
            run("CLS", shell=True)
            print(T1.render(menu=repositories, title="Available audio repositories."))
            answer = input(" Please choose source repository or press [Q] to quit: ")
            if answer.upper() == "Q":
                q_pressed, level = True, 100
                break
            try:
                repository = repositories[int(answer) - 1]
            except (ValueError, IndexError):
                continue
            else:
                if not int(answer):
                    continue
                repository = configuration["repositories"][repository]
                extensions = configuration["extensions"][configuration["compression"][repository]]
                artists = OrderedDict(sorted(get_artists(), key=itemgetter(0)))
                selectors = OrderedDict((name, has_extension(path, *extensions)) for name, path in artists.items())
                selectors = list(zip(*selectors.items()))
                menu = list(itertools.compress(data=selectors[0], selectors=selectors[1]))
                step += 1
                break

    #    ---------------
    # B. Pick up artist.
    #    ---------------
    elif step == 2:
        if not repository:
            run("CLS", shell=True)
            print(T1.render(menu=[]))
            input(" An issue occurred: repository is missing. Press any key to quit.")
            q_pressed, level = True, 1
        if not artists:
            run("CLS", shell=True)
            print(T1.render(menu=[]))
            input(" An issue occurred: artists are missing. Press any key to quit.")
            q_pressed, level = True, 2
        if not menu:
            run("CLS", shell=True)
            print(T1.render(menu=[]))
            input(" An issue occurred: menu is missing. Press any key to quit.")
            q_pressed, level = True, 3
        if not q_pressed:
            while True:
                run("CLS", shell=True)
                print(T1.render(menu=menu, title="Available artists."))
                answer = input(" Please choose artist or press [Q] to quit: ")
                if answer.upper() == "Q":
                    q_pressed, level = True, 100
                    break
                try:
                    artist = menu[int(answer) - 1]
                except (ValueError, IndexError):
                    continue
                else:
                    if not int(answer):
                        continue
                    artist = artists[artist]
                    destination = os.path.join(repository, os.path.splitdrive(artist)[1][1:])
                    albums = OrderedDict((album, (path, albumsort)) for album, path, albumsort in sorted(get_albums(artist), key=itemgetter(2)))
                    selectors = OrderedDict((item[0], has_extension(item[1][0], *extensions)) for item in albums.items())
                    selectors = list(zip(*selectors.items()))
                    menu = list(itertools.compress(data=selectors[0], selectors=selectors[1]))
                    step += 1
                    break

    #     ------------------
    #  C. Pick up album.
    #     ------------------
    elif step == 3:
        if not artist:
            run("CLS", shell=True)
            print(T1.render(menu=[]))
            input(" An issue occurred: artist is missing. Press any key to quit.")
            q_pressed, level = True, 4
        if not q_pressed:

            if not menu:
                while True:
                    run("CLS", shell=True)
                    print(T1.render(menu=[]))
                    answer = input(" No albums found for {0}. Would you like to pick up another artist? Press [Y] for Yes or [N] for No. ".format(artist))
                    if answer.upper() not in ACCEPTEDANSWERS:
                        continue
                    if answer.upper() == "N":
                        q_pressed, level = True, 100
                    elif answer.upper() == "Y":
                        step = 2
                    break

            elif menu:
                while True:
                    run("CLS", shell=True)
                    print(T1.render(menu=menu, title="Available albums."))
                    answer = input(" Please choose album or press [Q] to quit: ")
                    if answer.upper() == "Q":
                        q_pressed, level = True, 100
                        break
                    try:
                        album = menu[int(answer) - 1]
                    except (ValueError, IndexError):
                        continue
                    else:
                        if not int(answer):
                            continue
                        source = albums[album][0]
                        albumsort = albums[album][1]
                        destination = os.path.join(destination, albumsort)
                        arguments.append((source, destination, extensions))
                        step += 1
                        break

    #    ----------------
    # F. Add other albums.
    #    -----------------
    elif step == 4:
        if not source:
            run("CLS", shell=True)
            print(T1.render(menu=[]))
            input(" An issue occurred: source directory is missing. Press any key to quit.")
            q_pressed, level = True, 5
        if not destination:
            run("CLS", shell=True)
            print(T1.render(menu=[]))
            input(" An issue occurred: destination directory is missing. Press any key to quit.")
            q_pressed, level = True, 6
        if not q_pressed:
            while True:
                run("CLS", shell=True)
                print(T1.render(menu=[]))
                answer = input(" Would you like to pick up another album? Press [Y] for Yes or [N] for No. ")
                if answer.upper() not in ACCEPTEDANSWERS:
                    continue
                if answer.upper() == "N":
                    step += 1
                elif answer.upper() == "Y":
                    source, destination, step = init()
                break

    #    ---------------
    # G. Confirm copies.
    #    ---------------
    elif step == 5:
        while True:
            run("CLS", shell=True)
            print(T1.render(menu=[]))
            answer = input(" Would you like to copy files? Press [Y] for Yes or [N] for No. ")
            if answer.upper() not in ACCEPTEDANSWERS:
                continue
            if answer.upper() == "N":
                level = 100
            copy, q_pressed = True, True
            break

# ===========================
# Create DOS command(s) file.
# ===========================
if copy:
    for source, destination, extensions in arguments:
        for dirname, dirnames, filenames in os.walk(source):
            if not dirnames:
                if filenames:
                    if has_extension(dirname, *extensions):
                        collection.extend([(os.path.join(dirname, "*.{0}".format(extension)), destination) for extension in extensions])
    args.outfile.write(T2.render(collection=collection))

# ============
# Exit script.
# ============
run("CLS", shell=True)
sys.exit(100)
