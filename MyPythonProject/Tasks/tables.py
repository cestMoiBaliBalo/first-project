# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import os
from itertools import groupby
from operator import itemgetter
from pathlib import Path
from typing import Any

from Applications.Tables.shared import DatabaseConnection
from Applications.shared import TemplatingEnvironment, rjustify, stringify

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent

parser = argparse.ArgumentParser()
parser.add_argument("table", choices=["applications", "countries", "genres", "languages", "providers", "supports"], nargs="+")
arguments = parser.parse_args()

ENVIRONMENT = TemplatingEnvironment(_MYPARENT / "Templates")
ENVIRONMENT.set_environment(filters={"rjustify": rjustify,
                                     "stringify": stringify})
MAPPING = {"applications": "SELECT applicationid, application FROM applications ORDER BY application",
           "countries": "SELECT countryid, country FROM countries ORDER BY country",
           "genres": "SELECT genreid, genre FROM genres ORDER BY genre",
           "languages": "SELECT languageid, language FROM languages ORDER BY language",
           "providers": "SELECT providerid, provider FROM providers ORDER BY provider",
           "repositories": "SELECT repositoryid, repository FROM repositories ORDER BY repository",
           "supports": "SELECT supportid, support FROM supports ORDER BY support"}

collection = []  # type: Any
for table in arguments.table:
    with DatabaseConnection() as conn:
        collection.extend([(table, row[1]) for row in conn.execute(MAPPING[table])])
if collection:
    print(ENVIRONMENT.get_template("T01").render(collection=groupby(sorted(collection, key=itemgetter(0)), key=itemgetter(0))))
