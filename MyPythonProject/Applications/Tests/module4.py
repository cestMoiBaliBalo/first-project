# -*- coding: utf-8 -*-
import json
import os
import unittest

from ..shared import StringFormatter

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"


class Test01(unittest.TestCase):
    def setUp(self):
        self.stringformatter = StringFormatter()
        with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "StringFormatter.json")) as fp:
            self.thatlist = json.load(fp)

    def test_01first(self):
        for inp_string, out_string in self.thatlist:
            self.assertEqual(self.stringformatter.convert(inp_string), out_string)
