import argparse

def database(db: str) -> str: ...
def unixtime(timestamp) -> int: ...


class SetDatabase(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs) -> None: ...
    def __call__(self, parser, namespace, values, option_string=...) -> None: ...


database_parser = ...
epochconverter = ...
loglevel_parser = ...
subset_parser = ...
tags_grabber = ...
tasks_parser = ...
zipfile = ...
