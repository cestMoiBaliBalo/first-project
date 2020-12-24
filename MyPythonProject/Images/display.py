# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import csv
import locale
import os
from functools import partial
from itertools import chain, compress
from operator import attrgetter, itemgetter
from pathlib import Path
from typing import Any

from dateutil.parser import parse

from Applications.decorators import itemgetter_
from Applications.shared import CustomDialect, LOCAL, TEMPLATE2, TemplatingEnvironment, UTF8, format_date, rjustify_index

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")

# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("collection", type=argparse.FileType(encoding=UTF8))
arguments = parser.parse_args()

# ================
# Local functions.
# ================
rjustify = partial(rjustify_index, width=4)

# =======================
# Templating environment.
# =======================
template = TemplatingEnvironment(_MYPARENT / "Templates")
template.set_environment(filters={"rjustify": rjustify})

# ============
# Main script.
# ============
stream = csv.reader(arguments.collection, CustomDialect())
collection = [(Path(image),
               format_date(LOCAL.localize(parse(datetime.replace(":", '-', 2))), template=TEMPLATE2),
               int(parse(datetime.replace(":", '-', 2)).timestamp())) for image, datetime in stream]  # type: Any
collection = sorted(collection, key=itemgetter(2))
collection = sorted(collection, key=itemgetter_(0)(attrgetter("parent")))
collection = enumerate(collection, start=1)
collection = [((index,), tuple(compress(file, [1, 1, 0]))) for index, file in collection]
collection = [tuple(chain.from_iterable(item)) for item in collection]
print(template.get_template("T01").render(collection=collection))
