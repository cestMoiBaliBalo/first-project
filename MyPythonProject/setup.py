# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
from setuptools import find_packages, setup

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

setup(name='MyPythonProject',
      version='0.0.1',
      description="",
      author="",
      author_email="",
      url="",
      packages=find_packages(),
      package_data={"Applications.Unittests": ["Resources/*.yml", "Resources/*.json"]}, install_requires=['PyYAML', 'jinja2', 'dateutil']
      )
