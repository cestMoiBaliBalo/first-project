import argparse
from typing import Any

database_parser = ...  # type: Any
tags_grabber = ...  # type: Any
tasks_parser = ...  # type: Any


class Database(object):
    def __init__(self): ...
    def __call__(self, db: str) -> str: ...


class SetDatabase(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs) -> None: ...
    def __call__(self, parsobj, namespace, values, option_string=...) -> None: ...
