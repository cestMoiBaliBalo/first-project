# -*- coding: utf-8 -*-
import logging.config
import os
from subprocess import run

import yaml

from Applications.shared import DATABASE, TESTDATABASE, prettyprint

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))


# ==========
# Functions.
# ==========
def prompt_databases(template):
    """

    :param template:
    :param iterable:
    :return:
    """
    DATABASES = {"Test database": TESTDATABASE, "Production database (default)": DATABASE}
    database = None
    while True:
        run("CLS", shell=True)
        print(template.render(menu=sorted(DATABASES, reverse=True), logs=[], title="Available databases."))
        answer = input(" Please choose database or press [Q] to quit: ")
        if answer.upper() == "Q":
            break
        if answer == "":
            answer = "2"
        try:
            database = sorted(DATABASES, reverse=True)[int(answer) - 1]
        except (ValueError, IndexError):
            continue
        else:
            database = DATABASES[database]
            break
    return database


def prompt_logs(template, *iterable):
    """

    :param template:
    :param iterable:
    :return:
    """
    pages, page, previous_page = len(iterable), 1, 0
    collection, logs = [], []
    while True:
        if page != previous_page:
            previous_page = page
            logs = list(prettyprint(*filter(None, iterable[page - 1])))[1]

        run("CLS", shell=True)
        print(template.render(menu=[], logs=logs, title="Available logs."))
        prompt, allowed = set_prompt(page, pages, bool(len(collection)))
        answer = input(prompt)
        try:
            answer = int(answer)
        except ValueError:
            if answer.upper() not in allowed:
                continue
            if answer.upper() == "D":
                break
            elif answer.upper() == "N":
                page += 1
                continue
            elif answer.upper() == "P":
                page -= 1
                continue
            elif answer.upper() == "Q":
                collection = []
                break
        else:
            try:
                log = iterable[page - 1][answer - 1][-1]
            except (ValueError, IndexError):
                continue
            else:
                if not answer:
                    continue
                collection.append(log)
    return collection


def set_prompt(requested_page, total_pages, promptd):
    """

    :param requested_page:
    :param total_pages:
    :param promptd:
    :return:
    """
    _prompt, _promptD, _promptN, _promptP, _promptQ = "Please choose log", ", press [D] to delete the chosen log(s)", "", "", " or press [Q] to quit: "
    _allowed = ["Q"]
    if promptd:
        _prompt = "{0}{1}".format(_prompt, _promptD)
        _allowed.append("D")
    if total_pages > 1:
        if requested_page < total_pages:
            _promptN = ", press [N] for next page"
        if requested_page > 1:
            _promptP = ", press [P] for previous page"
    if _promptN:
        _prompt = "{0}{1}".format(_prompt, _promptN)
        _allowed.append("N")
    if _promptP:
        _prompt = "{0}{1}".format(_prompt, _promptP)
        _allowed.append("P")
    return " {0}{1}".format(_prompt, _promptQ), sorted(_allowed)
