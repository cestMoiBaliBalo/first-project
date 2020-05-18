# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import csv
import os
import re
import sys
from itertools import compress, groupby
from operator import itemgetter
from pathlib import Path
from typing import Any, Iterator, List, Mapping, Tuple, Union

from dateutil.parser import parse

from Applications.callables import match_
from Applications.decorators import itemgetter_, map_
from Applications.shared import CustomDialect, TemplatingEnvironment

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYPARENT = Path(os.path.abspath(__file__)).parent


# ==============
# Local classes.
# ==============
class CompilePattern(argparse.Action):
    """

    """

    def __init__(self, option_strings, dest, **kwargs):
        super(CompilePattern, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, re.compile(values, re.IGNORECASE))


# ================
# Local functions.
# ================
def get_parts(path: Union[str, Path]) -> Tuple[str, ...]:
    return Path(path).parts


def get_timestamp(timestr: str) -> int:
    return int(parse(timestr).timestamp())


def format_index_(index: int) -> str:
    return "{0:>5d}".format(index)


def format_(*iterables: Tuple[str, ...]) -> Iterator[Tuple[str, int]]:
    """

    :param iterables:
    :return:
    """

    # 1. Compress collection. Keep only file and last change UTC date.
    collection = [tuple(compress(file, [0, 0, 1, 1, 0])) for file in iterables]  # type: Any

    # 2. Filter collection. Keep only FLAC files.
    collection = filter(itemgetter_(0)(match_(arguments.pattern.search)), collection)

    # 3. Convert last change UTC date into timestamp.
    collection = zip(*map_(1)(get_timestamp)(*zip(*collection)))

    # 4. Remove duplicate files. Keep only the most recent last change UTC date for every file.
    collection = {key: list(group) for key, group in groupby(collection, key=itemgetter(0))}
    for key, values in collection.items():
        collection[key] = values
        if len(values) > 1:
            collection[key] = [(key, max(itemgetter(1)(value))) for value in values]

    # 5. Yield collection content.
    for _, container in collection.items():
        for file, ts in container:
            yield file, ts


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("files", type=argparse.FileType(encoding="ISO-8859-1"))
parser.add_argument("pattern", action=CompilePattern)
parser.add_argument("--pprint", action="store_true")

# =======================
# Templating environment.
# =======================
environment = TemplatingEnvironment(_MYPARENT)
environment.set_environment(filters={"format_": format_index_})

# ===========
# Main logic.
# ===========

# Initialize variables.
content, level = [], 100  # type: List[Any], int

# Get arguments.
arguments = parser.parse_args()

# Run script.
for target, group in groupby(csv.reader(arguments.files, CustomDialect()), key=itemgetter(0)):
    _content = []  # type: List[Any]
    sub_collection = {environment: list(sub_group) for environment, sub_group in groupby(group, itemgetter(1))}
    if {"BACKUP", "PRODUCTION"}.issubset(set(sub_collection.keys())):
        production = dict(("/".join(get_parts(file)[1:]), (ts, get_parts(file)[0])) for file, ts in format_(*sub_collection["PRODUCTION"]))  # type: Mapping[str, Tuple[int, str]]
        backup = dict(("/".join(get_parts(file)[3:]), ts) for file, ts in format_(*sub_collection["BACKUP"]))  # type: Mapping[str, int]
        _target = f"Target: {target}."
        _separator = "=" * len(_target)
        _content.extend([_separator, _target, _separator])

        # Get appended files.
        app_files = [Path(production[item][1]) / item for item in sorted(set(production).difference(backup))]
        if len(app_files) == 0:
            _content.extend(["No new file appended since the last backup.", None])
        if len(app_files) > 0:
            level = 0
            _content.extend([None, iter(app_files)])

        # Get modified files.
        chg_files = [Path(production[item][1]) / item for item in sorted(set(production).intersection(backup)) if production[item][0] > backup[item]]
        if len(chg_files) == 0:
            _content.extend(["No existing file modified since the last backup.", None])
        if len(chg_files) > 0:
            level = 0
            _content.extend([None, iter(chg_files)])

        # Append selected files to content template.
        content.append(tuple(_content))

# Output results.
if arguments.pprint:
    print(environment.get_template("check.tpl").render(contents=content))

# Exit script.
sys.exit(level)
