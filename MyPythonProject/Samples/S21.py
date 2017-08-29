# -*- coding: utf-8 -*-
import logging.config
import os

import yaml

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"


class Toto(object):
    def __init__(self, arg1, arg2, arg3, arg4):
        self._attr1 = None
        self._attr2 = None
        self._attr3 = None
        self._attr4 = None
        self.attr1 = arg1
        self.attr2 = arg2
        self.attr3 = arg3
        self.attr4 = arg4

    @property
    def attr1(self):
        return self._attr1

    @attr1.setter
    def attr1(self, arg):
        # Ici on peut faire des contrôles et lever des exceptions.
        if arg < 0:
            raise ValueError("{0} n\'est pas un argument admissible.".format(arg))
        self._attr1 = arg

    @property
    def attr2(self):
        return self._attr2

    @attr2.setter
    def attr2(self, arg):
        # Ici on peut faire des contrôles sans déclencher d'exception.
        self._attr2 = arg
        if arg < 0:
            self._attr2 = 0

    @property
    def attr3(self):
        return self._attr3

    @attr3.setter
    def attr3(self, arg):
        # Ici on peut faire des contrôles sans déclencher d'exception.
        self._attr3 = arg
        if arg < 100:
            self._attr3 = 100
        if arg > 1000:
            self._attr3 = 1000

    @property
    def attr4(self):
        return self._attr4

    @attr4.setter
    def attr4(self, arg):
        if arg == 0:
            raise ValueError("{0} n\'est pas un argument admissible.".format(arg))
        logger.debug(self._attr1)
        logger.debug(arg)
        self._attr4 = self._attr1 / arg


if __name__ == "__main__":

    with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
        logging.config.dictConfig(yaml.load(fp))
    logger = logging.getLogger("Applications.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))

    firstobject = Toto(1, 2, 3, 100)
    logger.debug(firstobject.attr1)  # 1
    logger.debug(firstobject.attr2)  # 2
    logger.debug(firstobject.attr3)  # 3
    logger.debug(firstobject.attr4)  # 0.01

    # On peut faire "firstobject.attr3 = 50" sans contredire les règles d'intégrité des attributs.
    # Cette affectation appelle en effet la méthode "attr3" qui effectue les contrôles d'intégrité.
    # l'algorithme récupère la valeur 100 en conséquence.
    # Les attributs sont ainsi encapsulés et non modifiables directement. On leur donne ainsi un aspect "privé" bien que cette notion n'existe pas au sens propre dans python.
    firstobject.attr3 = 50
    logger.debug(firstobject.attr3)  # 100 est affiché !

    for arg in [-100, 200]:
        try:
            firstobject.attr1 = arg
        except ValueError as err:
            logger.debug(err)  # "-100 n'est pas un argument admissible."
        else:
            logger.debug(firstobject.attr1)  # 200

    for arg in [0, 200]:
        try:
            firstobject.attr4 = arg
        except ValueError as err:
            logger.debug(err)  # "0 n'est pas un argument admissible."
        else:
            logger.debug(firstobject.attr4)  # 1.0
