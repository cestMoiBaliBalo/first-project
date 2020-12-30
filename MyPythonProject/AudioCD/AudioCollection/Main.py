# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import os
from pathlib import Path

import cherrypy

from Applications.cherrypy import DigitalAudioCollection

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent

if __name__ == '__main__':
    conf = {
        '/frameworks': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': str(_MYPARENT.parents[1] / "Resources" / "Frameworks")
        },
        '/scripts': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': str(_MYPARENT.parents[1] / "Resources" / "AudioCollection" / "Scripts")
        },
        '/stylesheets': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': str(_MYPARENT.parents[1] / "Resources" / "AudioCollection" / "Stylesheets")
        },
        '/images': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': str(_MYPARENT.parents[1] / "Resources" / "Images")
        },
        '/computing': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': str(_MYPARENT.parents[2])
        },
        '/albumart': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(os.path.expandvars("%_MYDOCUMENTS%"), "Album Art")
        }
    }

    cherrypy.tree.mount(DigitalAudioCollection(), '/audiocollection', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
