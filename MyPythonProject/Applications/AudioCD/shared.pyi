from collections.abc import MutableMapping
from contextlib import ContextDecorator
from pathlib import PureWindowsPath
from typing import Any, Iterable,IO, Mapping, Optional, Sequence, Tuple, Union


class AudioCDTags(MutableMapping):
    logger = ...  # type: Any
    track_pattern = ...  # type: Any
    def __init__(self) -> None: ...
    def __getitem__(self, item): ...
    def __setitem__(self, key, value): ...
    def __delitem__(self, key): ...
    def __len__(self) -> int: ...
    def __iter__(self): ...
    def __str__(self) -> str: ...


class ChangeAlbum(AudioCDTags):
    logger = ...  # type: Any
    def __init__(self, obj, template) -> None: ...


class ChangeAlbumArtist(TagsModifier):
    logger = ...  # type: Any
    def __init__(self, obj, albumartist: str) -> None: ...


class ChangeEncodedBy(TagsModifier):
    logger = ...  # type: Any
    def __init__(self, obj) -> None: ...


class ChangeMediaProvider(TagsModifier):
    logger = ...  # type: Any
    def __init__(self, obj, provider: str = ...) -> None: ...


class ChangeTotalTracks(TagsModifier):
    logger = ...  # type: Any
    def __init__(self, obj, totaltracks: int) -> None: ...


class ChangeTrack(TagsModifier):
    logger = ...  # type: Any
    def __init__(self, obj, offset: int) -> None: ...


class CommonAudioCDTags(AudioCDTags):
    logger = ...  # type: Any
    __tags = ...  # type: Mapping[str, bool]
    def __init__(self, sequence: str, **kwargs: Any) -> None: ...
    def __validatetags(self, **kwargs: Any) -> bool: ...


class DefaultAudioCDTags(AudioCDTags):
    logger = ...  # type: Any
    __tags = ...  # type: Mapping[str, bool]
    def __init__(self, sequence: str, **kwargs: Any) -> None: ...
    def __validatetags(self, **kwargs: Any) -> bool: ...


class BootlegAudioCDTags(AudioCDTags):
    logger = ...  # type: Any
    __tags = ...  # type: Mapping[str, bool]
    def __init__(self, sequence: str, **kwargs: Any) -> None: ...
    def __validatetags(self, **kwargs: Any) -> bool: ...


class RippedTrack(ContextDecorator):
    _environment = ...  # type: Any
    _outputtags = ...  # type: Any
    _tabs = ...  # type: int
    _in_logger = ...  # type: Any
    def __init__(self, rippingprofile: str, file, sequenc: str, *decoratingprofiles: str) -> None: ...
    @property
    def profile(self) -> str: ...
    @profile.setter
    def profile(self, arg: str) -> None: ...
    @property
    def decorators(self) -> Tuple[str]: ...
    @decorators.setter
    def decorators(self, arg: Tuple[str]) -> None: ...
    @property
    def tags(self): ...
    @tags.setter
    def tags(self, arg): ...
    @property
    def sequence(self) -> str: ...
    @sequence.setter
    def sequence(self, arg: str) -> None: ...
    @property
    def intags(self): ...
    @property
    def audiotrack(self): ...
    @staticmethod
    def get_tags(fil): ...
    @staticmethod
    def alter_tags(audiotrack, *decorators, **kwargs): ...
    def __enter__(self): ...
    def __exit__(self, exc_type, exc_val, exc_tb): ...


class TagsModifier(AudioCDTags):
    logger = ...  # type: Any
    def __init__(self, obj) -> None: ...


def album(track): ...
def albums(track: DefaultAudioCDTags, *, fil: Optional[str] = ..., encoding: str = ..., db: str = ...) -> Iterable[Tuple[str, Sequence[Union[int, str]]]]: ...
def bootlegs(track: BootlegAudioCDTags, *, fil: Optional[str] = ..., encoding: str = ..., db: str = ...) -> Iterable[Tuple[str, Sequence[Union[int, str]]]]: ...
def changealbum(obj, template): ...
def changealbumartist(obj, albumartist: str): ...
def changeencodedby(obj): ...
def changemediaprovider(obj): ...
def changetotaltracks(obj, totaltracks: int): ...
def changetrack(obj, offset: int): ...
def dump_audiotags_tojson(obj: DefaultAudioCDTags,
                          func: Callable[[DefaultAudioCDTags, Optional[str], str], Iterable[Tuple[str, Tuple[Any, ...]]]],
                          *,
                          database: str = ...,
                          jsonfile: Optional[str] = ...,
                          encoding: str = ...): ...
def dump_mapping_tojson(jsonfile: str, encoding: str = ..., **collection: Any) -> None: ...
def dump_sequence_tojson(jsonfile: str, *collection: Any, encoding: str = ...) -> None: ...
def dump_sequence_toyaml(yamlfile: str, *collection: Any, encoding: str = ...) -> None: ...
def dump_xreferences(track: Sequence[Union[bool, str]], *, fil: Optional[str] = None, encoding: str = ...) -> None: ...
def filcontents(fil) -> Iterable[str]: ...
def get_tagsfile(obj) -> str: ...
def get_xreferences(track: Union[PureWindowsPath, str]) -> Tuple[bool, Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], bool, Optional[str], Optional[str]]]: ...
def load_mapping_fromjson(jsonfile: str, encoding: str = ...) -> Iterable[Any]: ...
def load_sequence_fromjson(jsonfile: str, encoding: str = ...) -> Iterable[Any]: ...
def save_audiotags_sample(profile: str, *, samples: str = ..., **kwargs: Any) -> None: ...
def upsert_audiotags(profile: str, source: IO, sequence: str, *decorators: str, **kwargs: Any) -> Tuple[int, AudioCDTags]: ...
