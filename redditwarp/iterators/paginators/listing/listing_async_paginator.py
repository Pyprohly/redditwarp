
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Any, Dict, Optional, Callable, Sequence
if TYPE_CHECKING:
    from ....client_ASYNC import Client

from ..bidirectional_async_paginator import BidirectionalAsyncPaginator

T = TypeVar('T')

class ListingAsyncPaginator(BidirectionalAsyncPaginator[T]):
    def __init__(self,
        client: Client,
        uri: str, *,
        cursor_extractor: Callable[[Any], str] = lambda x: x['data']['name'],
    ):
        super().__init__()
        self.client = client
        self.uri = uri
        self.cursor_extractor = cursor_extractor
        self.count = 0
        self.show_all = False

    async def __anext__(self) -> Sequence[T]:
        if not self.has_next:
            raise StopAsyncIteration
        return await self._next_page()

    def _get_next_page_params(self) -> Dict[str, Optional[str]]:
        params: Dict[str, Optional[str]] = {
            'count': str(self.count),
            'limit': str(self.limit),
        }
        if self.show_all:
            params['show'] = 'all'

        if self._forward:
            params['after'] = self.cursor
        else:
            params['before'] = self.back_cursor

        remove_keys = [k for k, v in params.items() if v is None]
        for k in remove_keys: del params[k]
        return params

    async def _fetch_next_page_listing_data(self) -> Dict[str, Any]:
        params = self._get_next_page_params()
        recv = await self.client.request('GET', self.uri, params=params)
        data = recv['data']
        self.count += data['dist']
        entries = data['children']
        if entries:
            self.cursor = data['after'] or self.cursor_extractor(entries[-1])
            self.back_cursor = data['before'] or self.cursor_extractor(entries[0])

            has_after = bool(data['after'])
            has_before = bool(data['before'])
            if not self.get_direction():
                has_after, has_before = has_before, has_after
            self.has_next = has_after
            self.has_prev = has_before
        else:
            self.has_next = False

        return data

    async def _next_page(self) -> Sequence[T]:
        raise NotImplementedError

    def reset(self) -> None:
        super().reset()
        self.count = 0
