import argparse
from typing import Any


def database(db: str) -> str: ...


database_parser = ...  # type: Any
tags_grabber = ...  # type: Any
tasks_parser = ...  # type: Any


class ExcludeExtensions(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs) -> None: ...
    def __call__(self, parsobj, namespace, values, option_string=...) -> None: ...


class IncludeExtensions(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs) -> None: ...
    def __call__(self, parsobj, namespace, values, option_string=...) -> None: ...


class KeepExtensions(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs) -> None: ...
    def __call__(self, parsobj, namespace, values, option_string=...) -> None: ...


class SetDatabase(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs) -> None: ...
    def __call__(self, parsobj, namespace, values, option_string=...) -> None: ...


class SetEndSeconds(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs) -> None: ...
    def __call__(self, parsobj, namespace, values, option_string=...) -> None: ...
