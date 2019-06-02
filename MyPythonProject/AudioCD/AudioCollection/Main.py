# -*- coding: utf-8 -*-
# import logging.config
import os

import cherrypy

from Applications.cherrypy import DigitalAudioCollection

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

if __name__ == '__main__':
    # with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    #     logging.config.dictConfig(yaml.load(fp))
    # logger = logging.getLogger("Applications.Tables.RippedDiscs")

    conf = {
        '/frameworks': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Resources", "Frameworks")
        },
        '/scripts': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Resources", "AudioCollection", "Scripts")
        },
        '/stylesheets': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Resources", "AudioCollection", "Stylesheets")
        },
        '/images': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Resources", "Images")
        },
        '/computing': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.expandvars("%_COMPUTING%")
        },
        '/albumart': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(os.path.expandvars("%_MYDOCUMENTS%"), "Album Art")
        },
    }

    cherrypy.tree.mount(DigitalAudioCollection(), '/audiocollection', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
