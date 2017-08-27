# -*- coding: ISO-8859-1 -*-
import re
from operator import itemgetter

__author__ = 'Xavier ROSSET'


def myfunc1(s):
    rex = re.compile("([a-z]+)", re.IGNORECASE)
    return rex.split(s)


def myfunc2(s):
    rex = re.compile("([a-z]\d)", re.IGNORECASE)
    z = rex.split(s)
    if z[len(z)-1] == "":
        z[len(z)-1] = "0"
    return z


x = ("z10", "z100", "z50", "z1", "z2", "z200", "a62", "b73", "c53", "c109", "e20", "z20", "e1000", "m20", "x20", "c20", "nx46", "n345", "n234", "g46", "nxy46", "nxy50", "nxy20")


# ===============
# Tri par défaut.
# ===============
print("Default sort:\n{0}".format(sorted(x)))


# ===========================
# Tri par numéro puis lettre.
# ===========================
print("\n\nSort by number, then by letter:\n{0}".format(sorted(sorted(x, key=lambda i: myfunc1(i)[1]), key=lambda i: int(myfunc1(i)[2]))))


# ===========================
# Tri par lettre puis numéro.
# ===========================
print("\n\nSort by letter, then by number:\n{0}".format(sorted(sorted(x, key=lambda i: int(myfunc1(i)[2])), key=lambda i: myfunc1(i)[1])))
print("\n\nSort by reversed letter, then by number: \n{0}".format(sorted(sorted(x, key=lambda i: int(myfunc1(i)[2])), key=lambda i: myfunc1(i)[1], reverse=True)))
print("\n\nSort by letter, then by reversed number: \n{0}".format(sorted(sorted(x, key=lambda i: int(myfunc1(i)[2]), reverse=True), key=lambda i: myfunc1(i)[1])))
print("\n\nSort by reversed letter, then by reversed number: \n{0}".format(sorted(sorted(x, key=lambda i: int(myfunc1(i)[2]), reverse=True), key=lambda i: myfunc1(i)[1], reverse=True)))


# =============
# Tri exotique.
# =============
print("\n\nExotic sort:\n{0}".format(sorted(sorted(x, key=lambda i: myfunc2(i)[1]), key=lambda i: int(myfunc2(i)[2]))))


# =================
# Indexer un tuple.
# =================
templist2 = ["file1", "file2", "file3", "file4", "file5", "file6", "file7"]
templist3 = ["date1", "date2", "date3", "date3", "date1", "date4", "date3"]
print("\n\n{0}".format([(a, b, c) for a, (b, c) in enumerate(zip(templist2, templist3), start=1)]))


# ===============
# Trier un tuple.
# ===============
print("\n\n{0}".format(sorted(sorted([(a, b, c) for a, (b, c) in enumerate(zip(templist2, templist3), start=1)], key=itemgetter(1)), key=itemgetter(2), reverse=True)))
print("\n\n{0}".format(sorted(sorted([(a, b, c) for a, (b, c) in enumerate(zip(templist2, templist3), start=1)], key=itemgetter(1)), key=itemgetter(2), reverse=True)[:5]))
