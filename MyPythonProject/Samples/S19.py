# -*- coding: utf-8 -*-
import os.path

from cx_Freeze import Executable, setup

__author__ = 'Xavier ROSSET'

build_exe_options = {"build_exe": os.path.join(os.path.expandvars("%TEMP%"), "build")}
setup(name="toto",
      version="0.1",
      description="My first application!",
      options={"build_exe": build_exe_options},
      executables=[Executable(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Samples", "S18.py"))])
