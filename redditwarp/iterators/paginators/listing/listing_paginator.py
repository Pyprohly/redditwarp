
from __future__ import annotations
from typing import TypeVar
from typing import Sequence  # noqa: F401

from ..bidirectional_paginator import BidirectionalPaginator

P = TypeVar('P', bound='Sequence')

class ListingPaginator(BidirectionalPaginator[P]):
    def __init__(self) -> None:
        super().__init__()
        self.count = 0
        self.show_all = False
        self.include_subreddit_data = False
