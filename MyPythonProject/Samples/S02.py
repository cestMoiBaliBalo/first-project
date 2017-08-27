# -*- coding: utf-8 -*-
from contextlib import contextmanager, ContextDecorator, ExitStack
import os

__author__ = 'Xavier ROSSET'


# Fonction décorée par la fonction "contextmanager".
# La clause try... except... finally est utile pour interceptée les exceptions levées.
# Le texte "After" n'est pas restitué si une exception est levée mais n'est pas interceptée !
# A utiliser avec le mot clé "with" (voir l'exemple 1).
@contextmanager
def firstfunction():
    print("Before")
    try:
        yield
    except ValueError:
        print("Some error occurred.")
    finally:
        print("After")


# Deuxième fonction décorée par la fonction "contextmanager". Permet de modifier le répertoire en cours.
# A utiliser également avec le mot clé "with" (voir l'exemple 2).
@contextmanager
def secondfunction(p):
    x = os.getcwd()
    os.chdir(p)
    yield
    os.chdir(x)


# Fonction basique. Restitue le texte reçu.
def thirdfunction(p):
    print(p)


# Un context manager créé intégralement par définition des méthodes "__enter__" et "__exit__".
# Le texte "After" est systématiquement restitué même si une exception est levée.
# C'est la différence avec la fonction "firstfunction" !
# A utiliser également avec le mot clé "with".
# Voir l'exemple 6.
class FirstClass(object):

    def __enter__(self):
        print("Before")
        return self

    def __exit__(self, *exc):
        print("After")


class FourthClass(object):

    def __enter__(self):
        print("Before")
        raise ValueError("Value error!")

    def __exit__(self, *exc):
        print("After")


# Un context manager créé intégralement par définition des méthodes "__enter__" et "__exit__".
# A utiliser également avec le mot clé "with".
# Mais peut être aussi utilisé comme décorateur de fonction.
class SecondClass(ContextDecorator):

    def __enter__(self):
        print("Before")
        return self

    def __exit__(self, *exc):
        print("After")


# Une fonction basique décorée avec un context decorator.
# "decoratedfunction" est ainsi systématiquement modifiée (voir les exemples 3 et 4).
# Une fonction ne peut être en revanche modifiée qu'une seule fois en ne la décorant pas mais en associant le mot clé "with" au context decorator (voir l'exemple 5).
@SecondClass()
def decoratedfunction(p):
    print(p)


if __name__ == "__main__":

    print("# 1. ----- #")
    with firstfunction():
        thirdfunction("Some text.")
        raise ValueError("Some error occurred.")

    print("# 2. ----- #")
    print(os.getcwd())
    with secondfunction(os.path.expandvars("%_COMPUTING%")):
        print(os.getcwd())
    print(os.getcwd())

    print("# 3. ----- #")
    decoratedfunction("Some text 3")

    print("# 4. ----- #")
    decoratedfunction("Some text 4")

    print("# 5. ----- #")
    with SecondClass():
        thirdfunction("Some text 5")

    # print("# 6. ----- #")
    # with FirstClass():
    #     thirdfunction("Some text 2")
    #     raise ValueError("Some error occurred.")

    print("# 7. ----- #")
    stack = ExitStack()
    try:
        stack.enter_context(FourthClass())
    except ValueError as err:
        print(err)
    else:
        with stack:
            thirdfunction("Some text 6")

    print("# 8. ----- #")
    try:
        with FourthClass():
            thirdfunction("Some text 8")
    except ValueError as err:
        print(err)
