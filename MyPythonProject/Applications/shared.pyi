import argparse
from abc import ABC, abstractmethod
from contextlib import ContextDecorator, ExitStack, suppress
from datetime import date, datetime
from dateutil.parser import parserinfo
from functools import singledispatch
from pathlib import PurePath, PureWindowsPath, WindowsPath
from string import Template
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union

ACCEPTEDANSWERS = ...  # type: List[str]
ARTIST = ...  # type: str
APPEND = ...  # type: str
ARECA = ...  # type: str
BOOTLEGALBUM = ...  # type: str
CODEC = ...  # type: str
COMPRESSION = ...  # type: str
COPYRIGHT = ...  # type: str
DATABASE = ...  # type: str
DEFAULTALBUM = ...  # type: str
DFTDAYREGEX = ...  # type: str
DFTENCODING = ...  # type: str
DFTMONTHREGEX = ...  # ype: str
DFTTIMEZONE = ...  # type: str
DFTYEARREGEX = ...  # type: str
DISC = ...  # type: str
DRIVE = ...  # type: str
EXTENSIONS = ...  # type: Mapping[str, List[str]]
FILE = ...  # type: str
FOLDER = ...  # type: str
GENRES = ...  # type: List[str]
IMAGES = ...  # type: PurePath
IMAGES_COLLECTION = ...  # type: str
LETTER = ...  # type: str
LOCAL = ...  # type: Any
LOCALMONTHS = ...  # type: List[str]
LOGPATTERN = ...  # type: str
LOOKALBUMSORT = ...  # type: str
LOOKBOOTLEGALBUM = ...  # type: str
LOOKDEFAULTALBUM = ...  # type: str
LOOKEXTENSIONS = ...  # type: str
MUSIC = ...  # type: PurePath
TEMP = ...  # type: PurePath
TEMPLATE1 = ...  # type: str
TEMPLATE2 = ...  # type: str
TEMPLATE3 = ...  # type: str
TEMPLATE4 = ...  # type: str
TEMPLATE5 = ...  # type: str
TEMPLATE6 = ...  # type: str
TEMPLATE7 = ...  # type: str
TESTDATABASE = ...  # type: str
UPCREGEX = ...  # type: str
UTC = ...  # type: Any
UTF8 = ...  # type: str
UTF16 = ...  # type: str
UTF16BOM = ...  # type: str
WRITE = ...  # type: str
XREFERENCES = ...  # type: str


class ChangeLocalCurrentDirectory(ContextDecorator):
    def __init__(self, directory: Union[str, PurePath]): ...

    def __enter__(self): ...

    def __exit__(self, *exc): ...


class CustomTemplate(Template):
    def __init__(self, template: str) -> None: ...


class ExcludeExtensions(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs) -> None: ...

    def __call__(self, parsobj, namespace, values, option_string=...) -> None: ...


class GetExtensions(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs) -> None: ...

    def __call__(self, parsobj, namespace, values, option_string=...) -> None: ...


class GetPath(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs) -> None: ...

    def __call__(self, parsobj, namespace, values, option_string=...) -> None: ...


class IncludeExtensions(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs) -> None: ...

    def __call__(self, parsobj, namespace, values, option_string=...) -> None: ...


class KeepExtensions(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs) -> None: ...

    def __call__(self, parsobj, namespace, values, option_string=...) -> None: ...


class LocalParser(parserinfo):
    def __init__(self, dayfirst: bool = ..., yearfirst: bool = ...) -> None: ...


class SetDatabase(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs) -> None: ...

    def __call__(self, parsobj, namespace, values, option_string=...) -> None: ...


class SetEndSeconds(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs) -> None: ...

    def __call__(self, parsobj, namespace, values, option_string=...) -> None: ...


class TemplatingEnvironment(object):
    _environment = ...  # type: Any

    def __init__(self, path, keep_trailing_newline: bool = ..., trim_blocks: bool = ..., lstrip_blocks: bool = ...) -> None: ...

    def set_environment(self, **kwargs) -> None: ...

    def get_template(self, template: str): ...


class TitleCaseBaseConverter(ABC):
    config = ...  # type: Mapping[str, Union[List[str], bool]]
    acronyms = ...  # type: Any
    alw_lowercase = ...  # type: Any
    alw_uppercase = ...  # type: Any
    alw_capital = ...  # type: Any
    apostrophe_regex1 = ...  # type: Any
    apostrophe_regex2 = ...  # type: Any
    apostrophe_regex3 = ...  # type: Any
    apostrophe_regex4 = ...  # type: Any
    apostrophe_regex5 = ...  # type: Any
    apostrophe_regex6 = ...  # type: Any
    apostrophe_regex7 = ...  # type: Any
    capitalize_firstword = ...  # type: Any
    capitalize_lastword = ...  # type: Any
    capitalize_secondword = ...  # type: Any
    capitalize_words = ...  # type: Any
    punctuation = ...  # type: Any
    roman_numbers_regex1 = ...  # type: Any
    roman_numbers_regex2 = ...  # type: Any
    roman_numbers_regex3 = ...  # type: Any

    def __init__(self) -> None: ...

    @abstractmethod
    def convert(self, title: str) -> str: ...


class TitleCaseConverter(TitleCaseBaseConverter):
    _logger = ...  # type: Any

    def __init__(self) -> None: ...

    def convert(self, title: str) -> str: ...


class ToBoolean(object):
    def __init__(self, arg) -> None: ...

    @property
    def boolean_value(self) -> bool: ...


def adjust_datetime(year: int, month: int, day: int, hour: int, minutes: int, seconds: int) -> Optional[datetime]: ...


def attrgetter_(name: str): ...


def booleanify(arg): ...


def cjustify(strg: str, width: int, *, char: str = ...) -> str: ...


def convert_timestamp(timestamp: int, tz=...) -> datetime: ...


def copy(src: str, dst: str, *, size: int = ...) -> str: ...


def count_justify(*iterable: Tuple[str, int], length: int = ...) -> Tuple[str, str]: ...


def eq_string(a: str, b: str, *, sensitive: bool = ...) -> bool: ...


def find_files(directory: str, *, excluded=...): ...


def format_collection(collection: Iterable[Tuple[Any, ...]], *, tabsize: int = ..., gap: int = ..., group: Optional[int] = ...) -> Iterable[Tuple[str, ...]]: ...


def format_date(dt: Union[date, datetime], *, template: str = ...) -> str: ...


def get_albums(directory: Union[PureWindowsPath, WindowsPath, str]) -> Iterable[Tuple[str, str, str, bool]]: ...


def get_artists(directory: str = ...) -> Iterable[Tuple[str, str]]: ...


def get_dataframe(collection: Iterable[Tuple[Any, ...]], headers: List[str]): ...


def get_dirname(path: str, *, level: int = ...) -> str: ...


def get_drives() -> Iterable[str]: ...


def get_folders(directory: str) -> Iterable[Tuple[str, str]]: ...


def get_nearestmultiple(length: int, *, multiple: int = ...) -> int: ...


def get_readabledate(dt: datetime, *, template: str = ..., tz=...) -> str: ...


def get_rippingapplication(*, timestamp: Optional[int] = ...) -> str: ...


def get_tabs(length: int, *, tabsize: int = ...) -> str: ...


def grouper(iterable, n, *, fillvalue=...): ...


def int_(func): ...


def itemgetter_(*args: int): ...


def itemgetter2_(index: int = ...): ...


def left_justify(iterable: Iterable[Any]) -> Iterable[str]: ...


def localize_date(dt: datetime, tz=...) -> datetime: ...


def mainscript(strg: str, align: str = ..., fill: str = ..., length: int = ...) -> str: ...


def normalize(strg: str) -> str: ...


def normalize2(strg: str) -> str: ...


def not_(func): ...


def now(*, template: str = ...) -> str: ...


def partial_(*args, **kwargs): ...


def partitioner(iterable, *, predicate=...): ...


def print_collection(collection: Iterable[Tuple[Any, ...]], headers: Optional[Iterable[str]], *, char: str = ..., tabsize: int = ..., gap: int = ..., group: Optional[int] = ...) -> Iterable[str]: ...


def rjustify(strg: str, width: int, *, char: str = ...) -> str: ...


def sort_by_insertion(iterable: Iterable[Any], *, reverse: bool = ...) -> Iterable[Any]: ...


def stringify(arg) -> str: ...


def valid_albumid(albumid: str) -> str: ...


def valid_albumsort(albumsort: str) -> str: ...


def valid_database(database: str) -> str: ...


def valid_datetime(arg) -> Tuple[int, datetime, Tuple[int, int, int, int, int, int, int, int, int, str, int]]: ...


def valid_discnumber(discnumber: Union[int, str]) -> int: ...


def valid_genre(genre: str) -> str: ...


def valid_path(path: str) -> str: ...


def valid_productcode(productcode: str) -> str: ...


def valid_tracks(tracks: Union[int, str]) -> int: ...


def valid_year(year: Union[int, str]) -> int: ...
