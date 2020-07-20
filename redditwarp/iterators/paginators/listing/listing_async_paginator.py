
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Any, Dict
if TYPE_CHECKING:
    from ....client_sync import Client

from ..bidirectional_async_paginator import BidirectionalAsyncPaginator

T = TypeVar('T')

class ListingAsyncPaginator(BidirectionalAsyncPaginator[T]):
    def __init__(self, client: Client, uri: str) -> None:
        super().__init__()
        self.count = 0
        self.show_all = False
        self.include_subreddit_data = False
        self._client = client
        self._uri = uri

    async def _next_page_listing_data(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            'count': self.count,
            'limit': self.limit,
        }
        if self.show_all:
            params['show'] = 'all'
        if self.include_subreddit_data:
            params['sr_detail'] = '1'

        if self._forward:
            params['after'] = self.cursor
        else:
            params['before'] = self.back_cursor

        recv = await self._client.request('GET', self._uri, params=params)
        data = recv['data']

        self.cursor = data['after']
        self.back_cursor = data['before']
        self.count += data['dist']

        has_forward_cursor = bool(self.cursor)
        has_backward_cursor = bool(self.back_cursor)
        if self._forward:
            self.has_next = has_forward_cursor
            self.has_prev = has_backward_cursor
        else:
            self.has_next = has_backward_cursor
            self.has_prev = has_forward_cursor

        return data
