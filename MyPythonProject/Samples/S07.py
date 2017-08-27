# -*- coding: utf-8 -*-
from Applications.shared import DATABASE
import sqlite3

__author__ = 'Xavier ROSSET'


class Encoder(object):

    def __init__(self, name, code, folder, information):
        self._name = name
        self._code = code
        self._folder = folder
        self._information = information

    @property
    def name(self):
        return self._name

    @property
    def code(self):
        return self._code

    @property
    def folder(self):
        return self._folder

    @property
    def information(self):
        return self._information


def adapt_encoder(e):
    return "{0};{1};{2};{3}".format(e.name, e.code, e.folder, e.information).encode()


def convert_encoder(e):
    return Encoder(*[item.decode() for item in e.split(b";")])


if __name__ == "__main__":

    sqlite3.register_adapter(Encoder, adapt_encoder)
    sqlite3.register_converter("toto", convert_encoder)

    c = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
    c.row_factory = sqlite3.Row
    c.execute("DROP TABLE IF EXISTS encoders")
    c.execute("CREATE TABLE IF NOT EXISTS encoders (encoder TOTO NOT NULL)")
    c.execute("INSERT INTO encoders (encoder) VALUES (?)", (Encoder("FLAC", "13", "1.Lossless Audio Codec", "some informations"),))
    for row in c.execute("SELECT encoder FROM encoders ORDER BY encoder"):
        print(row["encoder"].name)
        print(row["encoder"].code)
        print(row["encoder"].folder)
        print(row["encoder"].information)
