# -*- coding: utf-8 -*-
"""
Tables.py: Command line application for tables maintenance.

Can be used as follow:

1. For displaying table record(s):
   select `table` --database "database_test.db"
   select `table`
   select `table` 250 251 252 --database "database_test.db"
   select `table` 250 251 252

2. For deleting table record(s):
   delete `table` 250 251 252 --database "database_test.db"
   delete `table` 250 251 252

3. For updating table record(s):
   update `table` 250 251 252 --artistsort "Artist, The" --albumsort "1.20170000.1" --database "database_test.db"
   update `table` 250 251 252 --artistsort "Artist, The" --albumsort "1.20170000.1"

"""
# pylint: disable=invalid-name

import argparse
from functools import partial
from itertools import chain, repeat
import logging.config
import os
import re
import sys
import yaml

import jinja2

from Applications.Database.AudioCD.shared import deletefromuid as deletelogfromuid, update as updatelog, select as selectlogs, selectfromuid as selectlogfromuid, validproductcode, validyear
from Applications.Database.DigitalAudioFiles.shared import deletealbumsfromuid, deletefromuid as deletealbumfromuid, updatealbum, selectalbums, selectfromuid as selectalbumfromuid
from Applications.shared import DATABASE, DFTDAYREGEX, DFTMONTHREGEX, DFTYEARREGEX, LOCAL, TEMPLATE4, UTC, readable, TemplatingEnvironment, validunixepochtime

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xav.python.computing@gmail.com'
__status__ = "Development"


# ===========
# Decorators.
# ===========
def func1(func):
    def wrapper(*args, db):
        albums = chain.from_iterable([[album.albumid for album in genobj] for genobj in map(func, args, repeat(db))])
        return list(chain.from_iterable([[row for row in genobj] for genobj in [selectalbums(db=db, albumid=album) for album in albums]]))

    return wrapper


def func2(func):
    def wrapper(*args, db):
        return list(map(func, args, repeat(db)))

    return wrapper


# ==========
# Functions.
# ==========
def gettemplate(args):
    """
    Get the appropriate Jinja2 template to display requested results.

    :param args: Namespace object holding parsed arguments as attributes.
    :return: Template. Or None if no template is required.
    """
    templates = {"rippinglog": {"select": {False: "T01",
                                           True: "T01"}},
                 "albums": {"select": {False: "T02",
                                       True: "T02"},
                            "delete": {False: "T03"}}}
    if args.table in templates:
        if args.statement in templates[args.table]:
            if args.donotpropagate in templates[args.table][args.statement]:
                return templates[args.table][args.statement][args.donotpropagate]
    return None


def albumsort(stg):
    """
    Check if a string match the albumsort pattern.

    :param stg: String.
    :return: Input string if match successes. Exception if match fails.
    """
    match1 = re.match(r"^[12]\.({0})({1})({2})\.\d$".format(DFTYEARREGEX, DFTMONTHREGEX, DFTDAYREGEX), stg)
    match2 = re.match(r"^[12]\.({0})0000\.\d$".format(DFTYEARREGEX), stg)
    if any([match1, match2]):
        return stg
    raise argparse.ArgumentTypeError('"{0}" isn\'t a correct albumsort tag.'.format(stg))


def select_func(ns=None, **kwargs):
    """
    Run the appropriate `select` function respective to the parsed table.

    :param ns: Namespace object holding parsed arguments as attributes.
    :param kwargs: Dictionary holding parsed arguments.
    :return: Selected records list.
    """

    # A namespace is provided.
    if ns:
        return list(selectrows[ns.table][bool(ns.rowid)](*ns.rowid, db=ns.db))

    # A dictionary is provided.
    db = kwargs.get("db")
    table = kwargs.get("table")
    rowid = kwargs.get("rowid")
    if all([db, table, rowid]):
        return list(selectrows[table][bool(rowid)](*rowid, db=db))

    return None


def delete_func(ns=None, **kwargs):
    """
    Run the appropriate `delete` function respective to the parsed table.

    :param ns: Namespace object holding parsed arguments as attributes.
    :param kwargs: Dictionary holding parsed arguments.
    :return: Deleted records count.
    """

    # A namespace is provided.
    if ns:
        child_logger = logging.getLogger("{0}.delete_func".format(os.path.splitext(os.path.basename(__file__))[0]))
        child_logger.debug(ns.table)
        child_logger.debug(ns.donotpropagate)
        child_logger.debug(deleterows[ns.table][ns.donotpropagate])
        return deleterows[ns.table][ns.donotpropagate](*ns.rowid, db=ns.db)

    # A dictionary is provided.
    db = kwargs.get("db")
    table = kwargs.get("table")
    rowid = kwargs.get("rowid")
    if all([db, table, rowid]):
        return deleterows[table][kwargs.get("donotpropagate", False)](*rowid, db=db)

    return 0


def update_func(**kwargs) -> int:
    """
    Run the appropriate `update` function respective to the parsed table.

    :param kwargs: Dictionary holding parsed arguments.
    :return: Updated records count.
    """
    db = kwargs.get("db")
    table = kwargs.get("table")
    rowid = kwargs.get("rowid")
    if all([db, table, rowid]):
        del kwargs["db"]
        del kwargs["table"]
        del kwargs["rowid"]
        if "statement" in kwargs:
            del kwargs["statement"]
        if "function" in kwargs:
            del kwargs["function"]
        if "template" in kwargs:
            del kwargs["template"]
        if kwargs:
            return updaterows[table](*rowid, db=db, **kwargs)
    return 0


# ===============
# Parent parsers.
# ===============

# -----
select_parent = argparse.ArgumentParser(description="Shared parser for `select` subparsers.", add_help=False)
select_parent.set_defaults(function=select_func)
select_parent.set_defaults(template=gettemplate)
select_parent.set_defaults(donotpropagate=False)
select_parent.add_argument("rowid", nargs="*", type=int, help="List of rows IDs to be selected. Optional.")

# -----
delete_parent = argparse.ArgumentParser(description="Shared parser for `delete` subparsers.", add_help=False)
delete_parent.set_defaults(function=delete_func)
delete_parent.set_defaults(template=gettemplate)
delete_parent.add_argument("rowid", nargs="+", type=int, help="List of rows IDs to be deleted. Mandatory.")

# -----
update_parent = argparse.ArgumentParser(description="Shared parser for `update` subparsers.", add_help=False, argument_default=argparse.SUPPRESS)
update_parent.set_defaults(function=update_func)
select_parent.set_defaults(donotpropagate=False)
update_parent.add_argument("rowid", nargs="+", type=int, help="List of rows IDs to be updated. Mandatory.")
update_parent.add_argument("--artist", help="Album artist. Optional.", metavar="The Artist")
update_parent.add_argument("--year", type=validyear, help="Album year. Optional. Only integers are allowed.")
update_parent.add_argument("--album", help="Album. Optional.", metavar="The Album")
update_parent.add_argument("--genre", choices=["Rock", "Hard Rock", "Progressive Rock", "Alternative Rock", "Heavy Metal", "Black Metal", "French Pop"], help="Album genre. Optional.")

# -----
database = argparse.ArgumentParser(description="Shared parser for database argument.", add_help=False)
database.add_argument("--database", dest="db", default=DATABASE, help="Path to database storing maintained tables.")

# ======================
# Main arguments parser.
# ======================


#     ------------
#  0. Main parser.
#     ------------
parser = argparse.ArgumentParser(usage="Command line application for tables maintenance.",
                                 description="Allow both `rippinglog` and `albums` maintenance thanks to a command line interface.",
                                 allow_abbrev=False,
                                 argument_default=argparse.SUPPRESS)
subparser = parser.add_subparsers(dest="table")

#     --------------------------------
#  1. Parser for `rippinglog` command.
#     --------------------------------
parser_log = subparser.add_parser("rippinglog", description="Subparser for `rippinglog` maintenance.")
subparser_log = parser_log.add_subparsers(dest="statement")

#  1.a. SELECT statement.
parser_log_select = subparser_log.add_parser("select", parents=[select_parent, database], description="Subparser for selecting record(s) from `rippinglog` table.")

#  1.b. DELETE statement.
parser_log_delete = subparser_log.add_parser("delete", parents=[delete_parent, database], description="Subparser for deleting record(s) from `rippinglog` table.")
parser_log_delete.set_defaults(donotpropagate=False)

#  1.c. UPDATE statement.
parser_log_update = subparser_log.add_parser("update", parents=[update_parent, database], description="Subparser for updating record(s) from `rippinglog` table.", argument_default=argparse.SUPPRESS)
parser_log_update.add_argument("--artistsort", help="Album artistsort key. Optional.", metavar="Artist, The")
parser_log_update.add_argument("--albumsort", type=albumsort, help="Album albumsort key. Optional.", metavar="1.20170000.1")
parser_log_update.add_argument("--upc", type=validproductcode, help="Album product code. Optional.")
parser_log_update.add_argument("--application", help="Ripping application. Optional.")
parser_log_update.add_argument("--ripped", type=validunixepochtime, help="Ripping Unix epoch time. Optional.", metavar="1500296048")
parser_log_update.set_defaults(template=gettemplate)

#     ----------------------------
#  2. Parser for `albums` command.
#     ----------------------------
parser_alb = subparser.add_parser("albums", description="Subparser for `albums` maintenance.")
subparser_alb = parser_alb.add_subparsers(dest="statement")

#  2.a. SELECT statement.
parser_alb_select = subparser_alb.add_parser("select", parents=[select_parent, database], description="Subparser for selecting record(s) from `albums` table.")

#  2.b. DELETE statement.
parser_alb_delete = subparser_alb.add_parser("delete", parents=[delete_parent, database], description="Subparser for deleting record(s) from `albums` table.")
parser_alb_delete.add_argument("--donotpropagate", nargs="?", default=False, const=True)

#  2.c. UPDATE statement.
# parser_alb_update = subparser_alb.add_parser("update", parents=[update_parent, database], description="Subparser for updating record(s) from `albums` table.")
# parser_alb_update.add_argument("--albumid", help="Album unique ID. Optional.", metavar="Artist, The.1.20170000.1")
# parser_alb_update.set_defaults(template=gettemplate)


# ===============
# Main algorithm.
# ===============
if __name__ == '__main__':

    # -----
    selectrows, deleterows, updaterows, mapping = {"rippinglog": {False: selectlogs,
                                                                  True: selectlogfromuid},
                                                   "albums": {False: selectalbums,
                                                              True: func1(selectalbumfromuid)}}, \
                                                  {"rippinglog": {False: deletelogfromuid,
                                                                  True: deletelogfromuid},
                                                   "albums": {False: func2(deletealbumfromuid),
                                                              True: deletealbumsfromuid}}, \
                                                  {"rippinglog": updatelog,
                                                   "albums": updatealbum}, \
                                                  {"delete": "deleted",
                                                   "update": "updated"}

    # -----
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        logging.config.dictConfig(yaml.load(fp))

    # -----
    TEMPLATE = TemplatingEnvironment(loader=jinja2.FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "AudioCD", "Tables")))
    TEMPLATE.set_environment(globalvars={"local": LOCAL,
                                         "utc": UTC},
                             filters={"readable": partial(readable, template=TEMPLATE4)})

    # -----
    arguments = parser.parse_args()

    # -----
    if arguments.template(arguments):
        print(TEMPLATE.environment.get_template(arguments.template(arguments)).render(content=arguments.function(ns=arguments)))
        sys.exit(0)
    print("{0} record(s) {1}".format(arguments.function(**{key: val for key, val in vars(arguments).items() if val}), mapping[arguments.statement]))
    sys.exit(0)
