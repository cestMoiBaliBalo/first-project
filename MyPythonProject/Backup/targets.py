# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import json
import locale
import os
from contextlib import ExitStack
from operator import itemgetter
from pathlib import Path
from typing import Any, Iterator, List, Tuple

from lxml import etree  # type: ignore

from Applications.decorators import itemgetter_
from Applications.shared import TemplatingEnvironment, UTF8, WRITE

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_THATFILE = Path(os.path.abspath(__file__))

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ==============
# Local classes.
# ==============
class GetPath(argparse.Action):
    """

    """

    def __init__(self, option_strings, dest, **kwargs):
        super(GetPath, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, list(map(Path, values)))


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("path", nargs="+", action=GetPath)
arguments = parser.parse_args()

# =========
# Template.
# =========
template = TemplatingEnvironment(_THATFILE.parent)

# ===============
# Main algorithm.
# ===============

# Get targets collection.
with ExitStack() as stack1:
    json_file = stack1.enter_context(open(_THATFILE.parent / "backup.json", mode=WRITE, encoding=UTF8))
    txt_file = stack1.enter_context(open(_THATFILE.parents[2] / "MyJavaProject" / "targets.txt", mode=WRITE, encoding="ISO-8859-1"))
    collection = []  # type: List[Tuple[Any, ...]]
    for argument in arguments.path:
        workspace = str(argument).split(".")[-1]
        with ExitStack() as stack2:
            targets = [stack2.enter_context(open(target, encoding=UTF8)) for target in os.scandir(argument) if target.is_file()]
            for target in targets:
                tree = etree.parse(target)
                root = tree.xpath("/target")[0]

                # Get target UID.
                uid = root.get("uid")

                # Get target name.
                name = root.get("name")

                # Get target source path.
                source = root.xpath("source")[0].get("path")

                # Get target destination path.
                destination = root.xpath("medium")[0].get("path").replace("//", "/")

                # Get target filters.
                regexes = [regex.get("rgpattern").replace("&gt;", ">") for regex in root.xpath("filter_group/regex_filter")]

                # Append target to collection.
                collection.append((workspace, uid, name, source, destination, regexes))

    # Sort targets collection.
    collection = sorted(collection, key=itemgetter_(1)(int))
    collection = sorted(collection, key=itemgetter(2))
    collection = sorted(collection, key=itemgetter(0))

    # Dump targets configuration into a JSON file.
    json.dump([dict([("workspace", workspace), ("description", name), ("target", uid)]) for workspace, uid, name, _, _, _ in collection], json_file, ensure_ascii=False, indent=4)

    # Dump targets configuration into a TXT file.
    main_content = []  # type: List[Tuple[str, str, str, Iterator[Iterator[Tuple[str, ...]]]]]
    for workspace, uid, name, source, destination, regexes in collection:
        if regexes:
            content = []  # type: List[Iterator[Tuple[str, ...]]]
            separator = "-" * (len(name) + 1)  # type: str
            for regex in regexes:
                content.append(iter([(uid, "PRODUCTION", source, regex), (uid, "BACKUP", destination)]))
            main_content.append((separator, f"{name}.", separator, iter(content)))
    txt_file.write(template.get_template("targets.tpl").render(content=iter(main_content)))
