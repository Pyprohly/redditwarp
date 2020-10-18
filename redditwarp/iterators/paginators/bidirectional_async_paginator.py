
from __future__ import annotations
from typing import TypeVar

from .async_paginator import AsyncPaginator

T = TypeVar('T')

class BidirectionalAsyncPaginator(AsyncPaginator[T]):
    @property
    def direction(self) -> bool:
        return self.get_direction()

    @direction.setter
    def direction(self, value: bool) -> None:
        self.set_direction(value)

    def __init__(self) -> None:
        super().__init__()
        self._direction = True

    def get_direction(self) -> bool:
        return self._direction

    def set_direction(self, value: bool) -> None:
        self._direction = value

    def change_direction(self) -> None:
        self.set_direction(not self._direction)
