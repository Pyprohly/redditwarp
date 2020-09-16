
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Any, Dict
if TYPE_CHECKING:
    from ....client_ASYNC import Client

from ..bidirectional_async_paginator import BidirectionalAsyncPaginator

T = TypeVar('T')

class ListingAsyncPaginator(BidirectionalAsyncPaginator[T]):
    def __init__(self, client: Client, uri: str) -> None:
        super().__init__()
        self.count = 0
        self.show_all = False
        self._client = client
        self._uri = uri

    def _get_next_page_params(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            'count': self.count,
            'limit': self.limit,
        }
        if self.show_all:
            params['show'] = 'all'

        if self._forward:
            params['after'] = self.cursor
        else:
            params['before'] = self.back_cursor

        return params

    async def _fetch_next_page_listing_data(self) -> Dict[str, Any]:
        params = self._get_next_page_params()
        recv = await self._client.request('GET', self._uri, params=params)
        data = recv['data']
        self.count += data['dist']
        c1 = data['after']
        c2 = data['before']
        self._set_cursors(c1, c2)
        return data
