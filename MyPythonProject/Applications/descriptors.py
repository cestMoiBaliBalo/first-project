# -*- coding: utf-8 -*-
from Applications.shared import DATABASE, DFTYEARREGEX, LOCAL, dateformat
from weakref import WeakKeyDictionary
import datetime
import os
import re

__author__ = 'Xavier ROSSET'


class Database(object):

    def __init__(self, default=DATABASE):
        self._default = default
        self._data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self._data.get(instance, self._default)

    def __set__(self, instance, value):
        argument = value
        if argument:
            argument = argument.replace('"', '')
        if argument and not(os.path.exists(argument) and os.path.isfile(argument)):
            raise ValueError('"{0}" isn\'t a valid database.'.format(argument))
        database = self._default
        if argument:
            database = argument
        self._data[instance] = database


class Integer(object):

    _regex = re.compile(r"\d+")

    def __init__(self, mandatory=True, default="0"):
        self._mandatory = mandatory
        self._default = default
        self._data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self._data.get(instance, [self._default])

    def __set__(self, instance, value):
        if self._mandatory and not value:
            raise ValueError('Please enter record(s) unique ID.')
        argument = self._default
        if value:
            argument = value
        argument = self._regex.findall(argument)
        if not argument:
            raise ValueError('Please enter coherent record(s) unique ID.')
        self._data[instance] = argument


class Year(object):

    _regex = re.compile(r"(?:{0})".format(DFTYEARREGEX))

    def __init__(self, mandatory=True):
        self._mandatory = mandatory
        self._default = dateformat(LOCAL.localize(datetime.datetime.utcnow()), "$Y")
        self._data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self._data.get(instance, [self._default])

    def __set__(self, instance, value):
        if self._mandatory and not value:
            raise ValueError("Please enter coherent year(s).")
        argument = self._default
        if value:
            argument = value
        argument = self._regex.findall(argument)
        if not argument:
            raise ValueError("Please enter coherent year(s).")
        self._data[instance] = argument


class Answers(object):

    def __init__(self, *acceptedanswers, default=None):
        self._acceptedanswers = list(acceptedanswers)
        self._default = default
        self._data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self._data.get(instance, self._default)

    def __set__(self, instance, value):
        if not value and not self._default:
            raise ValueError("Please enter answer.")
        answer = self._default
        if value:
            answer = value
        if answer not in self._acceptedanswers:
            raise ValueError('Please enter coherent answer. Only {0} are allowed.'.format(", ".join(self._acceptedanswers)))
        self._data[instance] = answer


class Folder(object):

    def __init__(self):
        self._data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self._data[instance]

    def __set__(self, instance, value):
        if not value:
            raise ValueError("Please enter directory.")
        directory = value.replace('"', '')
        if not os.path.exists(directory):
            raise ValueError('"{0}" doesn\'t exist'.format(directory))
        if not os.path.isdir(directory):
            raise ValueError('"{0}" is not a directory'.format(directory))
        if not os.access(directory, os.R_OK):
            raise ValueError('"{0}" is not a readable directory'.format(directory))
        self._data[instance] = directory


class File(object):

    def __init__(self, mandatory=True):
        self._mandatory = mandatory
        self._data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self._data[instance]

    def __set__(self, instance, value):
        if self._mandatory and not value:
            raise ValueError("Please enter an existing file. Both dirname and basename.")
        if value:
            value = value.replace('"', '')
            if not os.path.exists(value):
                raise ValueError('"{0}" doesn\'t exist. Please enter an existing file. Both dirname and basename.'.format(value))
            if not os.path.isfile(value):
                raise ValueError('"{0}" isn\'t a file. Please enter an existing file. Both dirname and basename.'.format(value))
            if not os.access(value, os.R_OK):
                raise ValueError('"{0}" is not a readable file.'.format(value))
        self._data[instance] = value


class Extensions(object):

    _regex = re.compile(r"\w+")

    def __init__(self, mandatory=False):
        self._mandatory = mandatory
        self._data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self._data[instance]

    def __set__(self, instance, value):
        if self._mandatory and not value:
            raise ValueError('Please enter extension(s).')
        argument = self._regex.findall(value)
        if self._mandatory and not argument:
            raise ValueError('Please enter coherent extension(s).')
        self._data[instance] = argument
