from functools import partial
from pathlib import Path
from typing import Any, Callable, Iterable, Optional, Set

filter_audiofiles = ...  # type: Callable[[Path, Iterable[str]], Set[Path]]
filter_losslessaudiofiles = ...  # type: Callable[[Path, Iterable[str]], Set[Path]]
filter_portabledocuments = ...  # type: partial[[Path, Iterable[str]]]


def filterfalse_(func) -> Callable[[Path, Iterable[str]], Set[Path]]: ...
def filter_extension(cwdir: Path, *names: str, extension: Optional[str] = ...) -> Set[str]: ...
def filter_extensions(*extensions: str) -> Callable[[Path, Iterable[str]], Set[Path]]: ...
def group_(index: int = ...): ...
def match_(func): ...
