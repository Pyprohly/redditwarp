
import pytest

from typing import Sequence, Any, Optional, Mapping, MutableMapping
from redditwarp.client_ASYNC import Client
from redditwarp.core.http_client_ASYNC import HTTPClient
from redditwarp.http.base_session_ASYNC import BaseSession
from redditwarp.http.request import Request
from redditwarp.http.response import Response
from redditwarp.http.payload import Payload
from redditwarp.iterators.paginators.listing.listing_async_paginator import ListingAsyncPaginator

class MySession(BaseSession):
    async def send(self, request: Request, *, timeout: float = -1,
            aux_info: Optional[Mapping] = None) -> Response:
        return Response(0, {}, b'')

class MyHTTPClient(HTTPClient):
    session = MySession()

    def __init__(self,
        response_status: int,
        response_headers: Mapping[str, str],
        response_data: bytes,
    ) -> None:
        super().__init__(session=self.session)
        self.response_status = response_status
        self.response_headers = response_headers
        self.response_data = response_data

    async def request(self,
        verb: str,
        uri: str,
        *,
        params: Optional[MutableMapping[str, Optional[str]]] = None,
        payload: Optional[Payload] = None,
        data: Any = None,
        json: Any = None,
        headers: Optional[MutableMapping[str, str]] = None,
        timeout: float = 8,
        aux_info: Optional[Mapping] = None,
    ) -> Response:
        return Response(self.response_status, self.response_headers, self.response_data)

class MyListingPaginator(ListingAsyncPaginator[str]):
    async def __anext__(self) -> Sequence[str]:
        data = await self._fetch_next_page_listing_data()
        return [d['id'] for d in data['children']]


http = MyHTTPClient(200, {'Content-Type': 'application/json'}, b'')
client = Client.from_http(http)

@pytest.mark.asyncio
async def test_next_iteration_updates_fields() -> None:
    lp = MyListingPaginator(client, '/r/redditdev/top')
    assert lp.count == 0

    http.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "dist": 2,
        "children": [
            {"id": "1"},
            {"id": "2"}
        ],
        "after": "123",
        "before": null
    }
}
'''
    submissions = await lp.__anext__()
    assert len(submissions) == 2
    assert lp.cursor == '123'
    assert lp.back_cursor is None
    assert lp.has_next
    assert not lp.has_prev
    assert lp.count == 2

    http.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "modhash": null,
        "dist": 3,
        "children": [
            {"id": "3"},
            {"id": "4"},
            {"id": "5"}
        ],
        "after": "abc",
        "before": "456"
    }
}
'''
    await lp.__anext__()
    assert lp.cursor == 'abc'
    assert lp.back_cursor == '456'
    assert lp.has_next
    assert lp.has_prev
    assert lp.count == 5

@pytest.mark.asyncio
async def test_direction() -> None:
    lp = MyListingPaginator(client, '/r/redditdev/top')
    assert lp.get_direction()
    assert lp.has_next and not lp.has_prev
    lp.set_direction(True)
    assert lp.get_direction()
    assert lp.has_next and not lp.has_prev
    lp.set_direction(True)
    assert lp.has_next and not lp.has_prev
    lp.set_direction(False)
    assert not lp.get_direction()
    assert not lp.has_next and lp.has_prev
    lp.set_direction(False)
    assert not lp.has_next and lp.has_prev
    lp.change_direction()
    assert lp.get_direction()
    assert lp.has_next and not lp.has_prev
    lp.change_direction()
    assert not lp.get_direction()
    assert not lp.has_next and lp.has_prev

@pytest.mark.asyncio
async def test_has_next_and_has_prev() -> None:
    lp = MyListingPaginator(client, '/r/redditdev/top')
    assert lp.has_next and not lp.has_prev

    http.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "dist": 0,
        "children": [],
        "after": "asdf",
        "before": "zxcv"
    }
}
'''
    await lp.__anext__()
    assert lp.has_next and lp.has_prev

    http.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "dist": 0,
        "children": [],
        "after": null,
        "before": "zxcv"
    }
}
'''
    await lp.__anext__()
    assert not lp.has_next and lp.has_prev

@pytest.mark.asyncio
async def test_has_next_and_has_prev__backwards() -> None:
    lp = MyListingPaginator(client, '/r/redditdev/top')
    lp.change_direction()
    assert not lp.has_next and lp.has_prev

    http.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "dist": 0,
        "children": [],
        "after": "asdf",
        "before": "zxcv"
    }
}
'''
    await lp.__anext__()
    assert lp.has_next and lp.has_prev

    http.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "dist": 0,
        "children": [],
        "after": null,
        "before": "zxcv"
    }
}
'''
    await lp.__anext__()
    assert lp.has_next and not lp.has_prev
