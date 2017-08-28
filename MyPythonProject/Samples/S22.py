# -*- coding: utf-8 -*-

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"


class AudioCD(object):
    def __init__(self, artist):
        self._artist = None
        self.artist = artist

    @property
    def artist(self):
        return self._artist

    @artist.setter
    def artist(self, arg):
        if arg == "titi":
            raise ValueError("Error!")
        self._artist = arg


class DefaultAudioCD(object):
    def __init__(self, artist, year):
        self.audiocd = AudioCD(artist)
        self._year = None
        self.year = year

    def __getattr__(self, item):
        return getattr(self.audiocd, item)

    def __setattr__(self, key, value):
        if key == "artist":
            self.audiocd.__setattr__(key, value)
        super().__setattr__(key, value)

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, arg):
        self._year = arg


x = DefaultAudioCD("toto", 1984)
print(x.artist)
print(x.year)
try:
    x.artist = "tata"
except ValueError as err:
    print(err)
else:
    print(x.artist)
    print(x.year)
