# -*- coding: utf-8 -*-
import argparse
import operator
import os

from . import shared

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ==================
# Functions aliases.
# ==================
expandvars, join = os.path.expandvars, os.path.join


# =================
# Global Functions.
# =================
def database(db: str) -> str:
    """

    :param db:
    :return:
    """
    try:
        _database = shared.valid_database(db)
    except ValueError as err:
        raise argparse.ArgumentTypeError(err)
    return _database


# =======================
# Custom parsing actions.
# =======================
class SetDatabase(argparse.Action):
    """

    """

    def __init__(self, option_strings, dest, **kwargs):
        super(SetDatabase, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        if values:
            setattr(namespace, "db", shared.TESTDATABASE)


class ExcludeExtensions(argparse.Action):
    """
    Set "exclude" attribute with a list of extensions to exclude.
    Set "extensions" attribute with a list of extensions to process.
    """

    def __init__(self, option_strings, dest, **kwargs):
        super(ExcludeExtensions, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        lext = []
        for ext in getattr(namespace, "extensions"):
            if ext not in values:
                lext.append(ext)
        setattr(namespace, "extensions", lext)


class KeepExtensions(argparse.Action):
    """
    Set "retain" attribute with a list of extensions to retain.
    Set "extensions" attribute with a list of extensions to process.
    """

    def __init__(self, option_strings, dest, **kwargs):
        super(KeepExtensions, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        lext = []
        for ext in values:
            if ext in getattr(namespace, "extensions"):
                lext.append(ext)
        setattr(namespace, "extensions", lext)


class IncludeExtensions(argparse.Action):
    """
    Set "include" attribute with a list of extensions to include.
    Set "extensions" attribute with a list of extensions to process.
    """

    def __init__(self, option_strings, dest, **kwargs):
        super(IncludeExtensions, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        lext = getattr(namespace, "extensions")
        for ext in values:
            if ext not in lext:
                lext.append(ext)
        setattr(namespace, "extensions", lext)


class SetEndSeconds(argparse.Action):
    """
    Set "end" attribute.
    """

    def __init__(self, option_strings, dest, **kwargs):
        super(SetEndSeconds, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        if not values:
            setattr(namespace, self.dest, getattr(namespace, "beg"))


#     =========
#  1. PARSER 1.
#     =========
database_parser = argparse.ArgumentParser(description="Shared parser for database arguments.", add_help=False)
group = database_parser.add_mutually_exclusive_group()
group.add_argument("--database", nargs="?", default=shared.DATABASE, help="Path to database storing digital albums.", type=database, dest="db")
group.add_argument("-t", "--test", nargs="?", default=False, const=True, action=SetDatabase, help="Use test database.")

#     =========
#  2. PARSER 2.
#     =========
tasks_parser = argparse.ArgumentParser()
tasks_parser.set_defaults(table="tasks")
tasks_parser.set_defaults(debug=True)
tasks_parser.add_argument("taskid", type=int)
subparser1 = tasks_parser.add_subparsers(dest="action")
parser_check = subparser1.add_parser("check", argument_default=argparse.SUPPRESS, parents=[database_parser])
parser_check.add_argument("--delta", default="10", type=int)
parser_update = subparser1.add_parser("update", argument_default=argparse.SUPPRESS, parents=[database_parser])
group = parser_update.add_mutually_exclusive_group()
group.add_argument("--timestamp", type=int)
group.add_argument("--datstring")
subparser2 = parser_update.add_subparsers(dest="operation")
parser_add = subparser2.add_parser("add", argument_default=argparse.SUPPRESS)
parser_add.set_defaults(func=operator.add)
parser_add.add_argument("days", type=int)
parser_sub = subparser2.add_parser("sub", argument_default=argparse.SUPPRESS)
parser_sub.set_defaults(func=operator.sub)
parser_sub.add_argument("days", type=int)

#     =========
#  3. PARSER 3.
#     =========
tags_grabber = argparse.ArgumentParser()
tags_grabber.add_argument("source", help="UTF16-LE with BOM encoded TXT audio tags file", type=argparse.FileType(mode="r+", encoding="UTF_16"))
tags_grabber.add_argument("profile", help="ripping profile", choices=["default", "bootleg", "live"])
tags_grabber.add_argument("sequence", help="audio encoder sequence")
tags_grabber.add_argument("decorators", nargs="*", help="decorating profile(s)")
tags_grabber.add_argument("--tags_processing", nargs="?", default="default", help="audio database processing profile")
