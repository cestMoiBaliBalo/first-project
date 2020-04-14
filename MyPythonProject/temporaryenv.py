# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
from subprocess import run
from tempfile import mkdtemp, mkstemp

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

tmpdir = mkdtemp()
_, ymltmp = mkstemp(dir=tmpdir)
_, txttmp = mkstemp(dir=tmpdir)
_, jsontmp = mkstemp(dir=tmpdir)
run(f"SETX _TMPDIR {tmpdir}")
run(f"SETX _TMPYML {ymltmp}")
run(f"SETX _TMPTXT {txttmp}")
run(f"SETX _TMPJSON {jsontmp}")
