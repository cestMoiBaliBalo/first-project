# -*- coding: utf-8 -*-
import logging.config
import os
import sqlite3
import sys
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
    :param db:
    :return:
    """
    records = []

    # Log arguments.
    int_logger = logging.getLogger("{0}.selectfrom".format(__name__))
    int_logger.debug("Database: {0}.".format(db))
    int_logger.debug("Table   : {0}.".format(table))

    # Configure sqlite statement.
    statement, placeholder, args = "SELECT * FROM {0} ORDER BY rowid".format(table), ["?"], ()
    if uid:
        statement = "SELECT * FROM {1} WHERE rowid IN ({0}) ORDER BY rowid".format(", ".join(placeholder * len(uid)), table)
        args = list(args)
        args.extend(uid)
    int_logger.debug(args)
    int_logger.debug(statement)

    # Grab records.
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    for row in conn.execute(statement, args):
        int_logger.debug("Record  :")
        int_logger.debug("\t{0}".format(row[0]).expandtabs(3))
        int_logger.debug("\t{0}".format(dateformat(UTC.localize(row[1]).astimezone(LOCAL), TEMPLATE4)).expandtabs(3))
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
    int_logger = logging.getLogger("{0}.selectfromuid".format(__name__))
    int_logger.debug("Database: {0}.".format(db))
    int_logger.debug("Table   : {0}.".format(table))
    int_logger.debug("ROWID   : {0:>3d}.".format(uid))

    # Grab record.
    try:
        return list(selectfrom(table, uid, db=db))[0]
    except IndexError:
        return ()


def insert(table, *uid, db=DATABASE, dtobj=None):
    """

    :param uid:
    :param db:
    :param table:
    :param dtobj:
    :return:
    """

    # Log arguments.
    int_logger = logging.getLogger("{0}.insert".format(__name__))
    int_logger.debug("Database: {0}.".format(db))
    int_logger.debug("Table   : {0}.".format(table))

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
        int_logger.exception(err)
    finally:
        status = conn.total_changes
        conn.close()
    int_logger.debug("{0:>3d} records inserted.".format(status))
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
    int_logger = logging.getLogger("{0}.update".format(__name__))
    int_logger.debug("Database: {0}.".format(db))
    int_logger.debug("Table   : {0}.".format(table))
    int_logger.debug("ROWID   : {0:>3d}.".format(uid))

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
        int_logger.debug("{0:>3d} records updated.".format(status))
        return status

    # Record doesn't exist: it is inserted.
    return insert(table, uid, db=db, dtobj=dtobj)


def deletefrom(table, db=DATABASE):
    """

    :param table:
    :param db:
    :return:
    """
    int_logger = logging.getLogger("{0}.delete".format(__name__))
    int_logger.debug("Database: {0}.".format(db))
    int_logger.debug("Table   : {0}.".format(table))
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
    int_logger.debug("{0:>3d} records removed.".format(status))
    return status


def deletefromuid(*uid, table, db=DATABASE):
    """

    :param uid:
    :param table:
    :param db:
    :return:
    """
    int_logger = logging.getLogger("{0}.deletefromuid".format(__name__))
    int_logger.debug("Database: {0}.".format(db))
    int_logger.debug("Table   : {0}.".format(table))
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
    int_logger.debug("{0:>3d} records removed.".format(status))
    return status


def isdeltareached(uid, table, *, db=DATABASE, days=10, create=True):
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

    arguments = tasks_parser.parse_args()

    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
        config = yaml.load(fp)
    for logger in ["Applications.Database.Tables"]:
        try:
            config["loggers"][logger]["level"] = arguments.loglevel
        except KeyError:
            pass
    logging.config.dictConfig(config)
    logger = logging.getLogger("Applications.Database.Tables")

    if arguments.action == "select":
        if getattr(arguments, "forced", False):
            sys.exit(0)
        d = {False: 1, True: 0}
        sys.exit(d[isdeltareached(arguments.taskid, arguments.table, db=arguments.db, days=arguments.days, create=not getattr(arguments, "dontcreate", False))])

    elif arguments.action == "update":
        sys.exit(update(arguments.taskid, arguments.table, db=arguments.db))
