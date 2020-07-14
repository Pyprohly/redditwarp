
from __future__ import annotations
from typing import TypeVar, Optional, Iterator
from typing import Sequence  # noqa: F401

from abc import ABC, abstractmethod

P = TypeVar('P', bound='Sequence')

class Paginator(Iterator[P], ABC):
    def __init__(self) -> None:
        self.limit = 0
        self.cursor: Optional[str] = None
        self.has_next = True

    def __iter__(self) -> Iterator[P]:
        return self

    @abstractmethod
    def __next__(self) -> P:
        raise NotImplementedError
