# -*- coding: utf-8 -*-
import logging
import sqlite3
from datetime import datetime, timedelta
from itertools import repeat

from ...shared import DATABASE, LOCAL, TEMPLATE4, UTC, dateformat

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

# =========
# Mappings.
# =========
MAPPING = {"tasks": ("taskid", "utc_run")}


# ===================================
# Main functions to work with tables.
# ===================================
def select(table, *, db=DATABASE):
    """

    :param table:
    :param db:
    :return:
    """
    records = []

    # Log arguments.
    logger = logging.getLogger("{0}.select".format(__name__))
    logger.debug("Database: {0}.".format(db))
    logger.debug("Table   : {0}.".format(table))

    # Get and yield records.
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    for row in conn.execute("SELECT * FROM {0} ORDER BY rowid".format(table)):
        logger.debug("Record  :")
        logger.debug("\t{0}".format(row[0]).expandtabs(3))
        logger.debug("\t{0}".format(dateformat(UTC.localize(row[1]).astimezone(LOCAL), TEMPLATE4)).expandtabs(3))
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
    logger = logging.getLogger("{0}.selectfromuid".format(__name__))
    logger.debug("Database: {0}.".format(db))
    logger.debug("Table   : {0}.".format(table))
    logger.debug("ID      : {0:>3d}.".format(uid))

    # Get and return record.
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    curs = conn.cursor()
    curs.execute("SELECT * FROM {0} WHERE rowid=?".format(table), (uid,))
    record = curs.fetchone()
    conn.close()
    return record


def insert(*uid, db=DATABASE, table=None, dtobj=None):
    """

    :param uid:
    :param db:
    :param table:
    :param dtobj:
    :return:
    """
    status = 0

    # Log arguments.
    logger = logging.getLogger("{0}.insert".format(__name__))
    logger.debug("Database: {0}.".format(db))
    logger.debug("Table   : {0}.".format(table))

    # Insert record.
    if table is None:
        return 0
    if table not in MAPPING:
        return 0
    if dtobj is None:
        dtobj = datetime.utcnow()
    conn = sqlite3.connect(db)
    try:
        with conn:
            conn.executemany("INSERT INTO {0} ({1}, {2}) VALUES(?, ?)".format(table, MAPPING[table][0], MAPPING[table][1]), zip(uid, repeat(dtobj)))
    except sqlite3.IntegrityError as err:
        logger.exception(err)
    else:
        status = conn.total_changes
        logger.debug("{0:>3d} records inserted.".format(status))
    finally:
        conn.close()
    return status


def update(uid, table, *, db=DATABASE, dtobj=None):
    """

    :param uid:
    :param table:
    :param db:
    :param dtobj:
    :return:
    """
    if table not in MAPPING:
        return 0
    if dtobj is None:
        dtobj = datetime.utcnow()
    record = selectfromuid(uid, table, db=db)

    # Record exists: it is updated.
    if record:
        status, conn = 0, sqlite3.connect(db)
        with conn:
            conn.execute("UPDATE {0} SET {1}=? WHERE rowid=?".format(table, MAPPING[table][1]), (dtobj, uid))
            status = conn.total_changes
        conn.close()
        return status

    # Record doesn't exist: it is inserted.
    return insert(uid, db=db, table=table, dtobj=dtobj)


def delete(table, db=DATABASE):
    """

    :param table:
    :param db:
    :return:
    """
    logger = logging.getLogger("{0}.delete".format(__name__))
    if table not in MAPPING:
        return 0
    status, conn = 0, sqlite3.connect(db)
    with conn:
        conn.execute("DELETE FROM {0}".format(table))
        status = conn.total_changes
        logger.debug("Database: {0}.".format(db))
        logger.debug("Table   : {0}.".format(table))
        logger.debug("{0:>3d} records removed.".format(status))
    conn.close()
    return status


def deletefromuid(*uid, table, db=DATABASE):
    """

    :param uid:
    :param table:
    :param db:
    :return:
    """
    logger = logging.getLogger("{0}.deletefromuid".format(__name__))
    if table not in MAPPING:
        return 0
    status, conn = 0, sqlite3.connect(db)
    with conn:
        conn.executemany("DELETE FROM {0} WHERE id=?".format(table), [(i,) for i in uid])
        status = conn.total_changes
        logger.debug("Database: {0}.".format(db))
        logger.debug("Table   : {0}.".format(table))
        logger.debug("{0:>3d} records removed.".format(status))
    conn.close()
    return status


def isdeltareached(uid, table, *, db=DATABASE, days=10):
    logger = logging.getLogger("{0}.isdeltareached".format(__name__))
    deltareached = True
    record = selectfromuid(uid, table, db=db)
    if record:
        if UTC.localize(datetime.utcnow()) - UTC.localize(record[1]) < timedelta(days=days):
            deltareached = False
    logger.debug(deltareached)
    return deltareached
