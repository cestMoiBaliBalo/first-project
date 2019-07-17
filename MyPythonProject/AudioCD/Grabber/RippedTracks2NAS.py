# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import itertools
import os
from contextlib import ExitStack
from pathlib import PurePath

from Applications.shared import TemplatingEnvironment, itemgetter_

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

that_file = PurePath(os.path.abspath(__file__))

# ==========
# Constants.
# ==========
COMPUTING = os.path.join(os.path.expandvars("%_COMPUTING%"))
RIPPEDTRACKS = "rippedtracks"


# ==========
# Functions.
# ==========
@itemgetter_()
def get_parent(path: str) -> PurePath:
    return PurePath(path).parent


@itemgetter_()
def get_name(path: str) -> str:
    return PurePath(path).name


# ============
# Main script.
# ============

# Define template.
template = TemplatingEnvironment(path=that_file.parents[1] / "Templates")
template.set_template(template="T02")

# Set copy commands file.
with ExitStack() as stack:
    fr = stack.enter_context(open(os.path.join(COMPUTING, "Resources", f"{RIPPEDTRACKS}.txt"), encoding="UTF_8"))
    fw = stack.enter_context(open(os.path.join(COMPUTING, "Resources", f"{RIPPEDTRACKS}.cmd"), mode="w", encoding="ISO-8859-1"))
    tracks = filter(None, itertools.chain.from_iterable([line.splitlines() for line in fr]))
    tracks = sorted(sorted((tuple(track.split("|")) for track in tracks), key=get_name), key=get_parent)
    tracks = [(src, PurePath(src).name, dst) for src, dst in tracks]
    fw.write(getattr(template, "template").render(collection=iter((key, list(group)) for key, group in itertools.groupby(tracks, key=get_parent))))
