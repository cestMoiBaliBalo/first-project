from typing import Iterable, Tuple

def aggregate_rippeddiscs_by_artistsort(db: str = ...) -> Iterable[Tuple[str, int]]: ...
def aggregate_rippeddiscs_by_genre(db: str = ...) -> Iterable[Tuple[str, int]]: ...
def aggregate_rippeddiscs_by_month(db: str = ...) -> Iterable[Tuple[str, int]]: ...
def aggregate_rippeddiscs_by_year(db: str = ...) -> Iterable[Tuple[str, int]]: ...
def delete_rippeddiscs(*uid: int, db: str = ...) -> int: ...
def get_rippeddiscs(db: str = ..., **kwargs): ...
def get_rippeddiscs_from_month(*month: int, db: str = ...): ...
def get_rippeddiscs_from_year(*year: int, db: str = ...): ...
def get_rippeddiscs_uid(db: str = ..., **kwargs) -> Iterable[Tuple[int, str, str, str, int, int, str, str]]: ...
def get_total_rippeddiscs(db: str = ...) -> int: ...