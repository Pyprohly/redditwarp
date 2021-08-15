
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Callable, Any, Iterable
if TYPE_CHECKING:
    from .....client_SYNC import Client

from ..listing_paginator import ListingPaginator

T = TypeVar('T')

class SubredditDetail(ListingPaginator[T]):
    def __init__(self,
        client: Client,
        uri: str,
        *,
        limit: Optional[int] = 100,
        cursor_extractor: Callable[[Any], str] = lambda x: x['data']['name'],
    ):
        super().__init__(client, uri, limit=limit, cursor_extractor=cursor_extractor)
        self.sr_detail = False

    def _generate_params(self) -> Iterable[tuple[str, Optional[str]]]:
        yield from super()._generate_params()
        if self.sr_detail:
            yield ('sr_detail', '1')
