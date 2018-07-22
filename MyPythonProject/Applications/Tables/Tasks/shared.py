# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import logging.config
import os
import sqlite3
import sys
from contextlib import suppress
from datetime import datetime, timedelta
from itertools import repeat

import yaml

from ...parsers import tasks_parser
from ...shared import DATABASE, LOCAL, TEMPLATE4, UTC, dateformat

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# =========
# Mappings.
# =========
MAPPING = {"tasks": ("taskid", "utc_run")}


# ===================================
# Main functions to work with tables.
# ===================================
def selectfrom(table, *uid, db=DATABASE):
    """

    :param table:
    :param uid:
    :param db:
    :return:
    """
    records = []

    # Log arguments.
    in_logger = logging.getLogger("Applications.Tables.Tasks.shared.selectfrom")
    in_logger.info("Database: %s", db)
    in_logger.info("Table   : %s", table)

    # Configure sqlite statement.
    statement, placeholder, args = "SELECT * FROM {0} ORDER BY rowid".format(table), ["?"], ()
    if uid:
        statement = "SELECT * FROM {1} WHERE rowid IN ({0}) ORDER BY rowid".format(", ".join(placeholder * len(uid)), table)
        args = list(args)
        args.extend(uid)
    in_logger.debug(statement)
    in_logger.debug(args)

    # Grab records.
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute(statement, args):
        in_logger.info("Record  :")
        in_logger.info("\t%s".expandtabs(3), row[0])
        in_logger.info("\t%s".expandtabs(3), dateformat(UTC.localize(row[1]).astimezone(LOCAL), TEMPLATE4))
        records.append(row)
    conn.close()
    for row in records:
        yield row


def selectfromuid(uid, table, *, db=DATABASE):
    """

    :param uid:
    :param table:
    :param db:
    :return:
    """

    # Log arguments.
    in_logger = logging.getLogger("Applications.Tables.Tasks.shared.selectfromuid")
    in_logger.debug("Database: %s", db)
    in_logger.debug("Table   : %s", table)
    in_logger.debug("ROWID   : %s", uid)

    # Grab record.
    record = ()
    with suppress(IndexError):
        record = list(selectfrom(table, uid, db=db))[0]
    return record


def insert(table, *uid, db=DATABASE, dtobj=None):
    """

    :param table:
    :param uid:
    :param db:
    :param dtobj:
    :return:
    """

    # Log arguments.
    in_logger = logging.getLogger("Applications.Tables.Tasks.shared.insert")
    in_logger.debug("Database: %s", db)
    in_logger.debug("Table   : %s", table)

    # Insert record.
    if table not in MAPPING:
        return 0
    if dtobj is None:
        dtobj = datetime.utcnow()
    conn = sqlite3.connect(db)
    try:
        with conn:
            conn.executemany("INSERT INTO {0} ({1}, {2}) VALUES(?, ?)".format(table, MAPPING[table][0], MAPPING[table][1]), zip(uid, repeat(dtobj)))
    except sqlite3.IntegrityError as err:
        in_logger.exception(err)
    finally:
        status = conn.total_changes
        conn.close()
    in_logger.debug("%s records inserted.", status)
    return status


def update(uid, table, *, db=DATABASE, dtobj=None):
    """

    :param uid:
    :param table:
    :param db:
    :param dtobj:
    :return:
    """

    # Log arguments.
    in_logger = logging.getLogger("Applications.Tables.Tasks.shared.update")
    in_logger.debug("Database: %s", db)
    in_logger.debug("Table   : %s", table)
    in_logger.debug("ROWID   : %s", uid)

    # Update record.
    if table not in MAPPING:
        return 0
    if dtobj is None:
        dtobj = datetime.utcnow()
    record = ()
    try:
        record = list(selectfrom(table, uid, db=db))[0]
    except IndexError:
        pass

    # Record exists: it is updated.
    if record:
        conn = sqlite3.connect(db)
        try:
            with conn:
                conn.execute("UPDATE {0} SET {1}=? WHERE rowid=?".format(table, MAPPING[table][1]), (dtobj, uid))
        except sqlite3.OperationalError:
            pass
        finally:
            status = conn.total_changes
            conn.close()
        in_logger.debug("%s records updated.", status)
        return status

    # Record doesn't exist: it is inserted.
    return insert(table, uid, db=db, dtobj=dtobj)


def deletefrom(table, db=DATABASE):
    """

    :param table:
    :param db:
    :return:
    """
    in_logger = logging.getLogger("Applications.Tables.Tasks.shared.delete")
    in_logger.debug("Database: %s", db)
    in_logger.debug("Table   : %s", table)
    if table not in MAPPING:
        return 0
    conn = sqlite3.connect(db)
    try:
        with conn:
            conn.execute("DELETE FROM {0}".format(table))
    except sqlite3.OperationalError:
        pass
    finally:
        status = conn.total_changes
        conn.close()
    in_logger.debug("%s records removed.", status)
    return status


def deletefromuid(*uid, table, db=DATABASE):
    """

    :param uid:
    :param table:
    :param db:
    :return:
    """
    in_logger = logging.getLogger("Applications.Tables.Tasks.shared.deletefromuid")
    in_logger.debug("Database: %s", db)
    in_logger.debug("Table   : %s", table)
    if table not in MAPPING:
        return 0
    conn = sqlite3.connect(db)
    try:
        with conn:
            conn.executemany("DELETE FROM {0} WHERE id=?".format(table), [(rowid,) for rowid in uid])
    except sqlite3.OperationalError:
        pass
    finally:
        status = conn.total_changes
        conn.close()
    in_logger.debug("%s records removed.", status)
    return status


def isdeltareached(uid, table, *, db=DATABASE, days=10, create=True):
    """

    :param uid:
    :param table:
    :param db:
    :param days:
    :param create:
    :return:
    """
    record = selectfromuid(uid, table, db=db)
    if record:
        return not UTC.localize(datetime.utcnow()) - UTC.localize(record[1]) < timedelta(days=days)
    if create:
        return bool(insert(table, uid, db=db))
    return False


# ===============================================
# Main algorithm if module is run as main script.
# ===============================================
if __name__ == "__main__":

    # Local constants.
    LEVELS = {False: "info", True: "debug"}
    EXIT = {False: 1, True: 0}

    # Get arguments.
    arguments = vars(tasks_parser.parse_args())

    # Configure logging.
    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
        config = yaml.load(fp)
    for logger in ["Applications.Tables.Tasks"]:
        with suppress(KeyError):
            config["loggers"][logger]["level"] = LEVELS[arguments.get("debug", False)].upper()
    logging.config.dictConfig(config)

    # Select task: can it be run?
    if arguments.get("action") == "select":
        sys.exit(EXIT[isdeltareached(arguments.get("taskid", 0),
                                     arguments.get("table", "tasks"),
                                     db=arguments.get("db", DATABASE),
                                     days=arguments.get("days", 10),
                                     create=not arguments.get("dontcreate", False))])

    # Update last run datetime task.
    elif arguments.get("action") == "update":
        sys.exit(update(arguments.get("taskid", 0),
                        arguments.get("table", "tasks"),
                        db=arguments.get("db", DATABASE)))
