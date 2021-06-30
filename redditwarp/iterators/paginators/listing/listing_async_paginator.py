
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Any, Dict, Optional, Callable, Sequence, cast
if TYPE_CHECKING:
    from ....client_ASYNC import Client

from ..cursor_bidirectional_async_paginator import CursorBidirectionalAsyncPaginator

T = TypeVar('T')

class ListingAsyncPaginator(CursorBidirectionalAsyncPaginator[T]):
    def __init__(self,
        client: Client,
        uri: str,
        *,
        limit: Optional[int] = 100,
        cursor_extractor: Callable[[Any], str] = lambda x: x['data']['name'],
    ):
        super().__init__()
        self.limit = limit
        self.client = client
        self.uri = uri
        self.cursor_extractor = cursor_extractor
        self.count = 0
        self.show_all = False

    def _get_params(self) -> Dict[str, str]:
        params: Dict[str, Optional[str]] = {
            'count': str(self.count),
            'limit': str(self.limit),
        }
        if self.show_all:
            params['show'] = 'all'
        if self.get_direction():
            params['after'] = self.forward_cursor
        else:
            params['before'] = self.backward_cursor
        remove_keys = [k for k, v in params.items() if v is None]
        for k in remove_keys: del params[k]
        return cast(Dict[str, str], params)

    async def _fetch_data(self) -> Dict[str, Any]:
        params = self._get_params()
        recv = await self.client.request('GET', self.uri, params=params)
        data = recv['data']
        self.count += dist if (dist := data['dist']) is not None else len(data['children'])
        entries = data['children']
        after = data['after']
        before = data['before']

        if entries:
            self.forward_cursor = after if after else self.cursor_extractor(entries[-1])
            self.backward_cursor = before if before else self.cursor_extractor(entries[0])

        self.forward_available = bool(after)
        self.backward_available = bool(before)
        return data

    async def _fetch_result(self) -> Sequence[T]:
        raise NotImplementedError

    async def next_result(self) -> Sequence[T]:
        self.resuming = False
        return await self._fetch_result()

    def reset(self) -> None:
        super().reset()
        self.count = 0
