
import pytest

from typing import Sequence, Any, Optional, Mapping, Callable
from redditwarp.client_ASYNC import Client
from redditwarp.core.http_client_ASYNC import HTTPClient
from redditwarp.http.base_session_ASYNC import BaseSession
from redditwarp.http.request import Request
from redditwarp.http.response import Response
from redditwarp.http.payload import Payload
from redditwarp.iterators.paginators.listing.listing_async_paginator import ListingAsyncPaginator

class MySession(BaseSession):
    async def send(self, request: Request, *, timeout: float = -1,
            aux_info: Optional[Mapping[Any, Any]] = None) -> Response:
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
        params: Optional[Mapping[str, Optional[str]]] = None,
        payload: Optional[Payload] = None,
        data: Any = None,
        json: Any = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: float = 8,
        aux_info: Optional[Mapping[Any, Any]] = None,
    ) -> Response:
        return Response(self.response_status, self.response_headers, self.response_data)

class MyListingPaginator(ListingAsyncPaginator[str]):
    def __init__(self,
        client: Client,
        uri: str,
    ):
        cursor_extractor: Callable[[Any], str] = lambda x: x['name']
        super().__init__(client, uri, cursor_extractor=cursor_extractor)

    async def _next_page(self) -> Sequence[str]:
        data = await self._fetch_next_page_listing_data()
        return [d['name'] for d in data['children']]


http = MyHTTPClient(200, {'Content-Type': 'application/json'}, b'')
client = Client.from_http(http)

@pytest.mark.asyncio
async def test_stop_iteration() -> None:
    p = MyListingPaginator(client, '')
    p.has_next = False
    http.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "dist": 2,
        "children": [
            {"name": "a"},
            {"name": "b"}
        ],
        "after": "b",
        "before": "a"
    }
}
'''
    with pytest.raises(StopAsyncIteration):
        await p.__anext__()

@pytest.mark.asyncio
async def test_return_value_and_count() -> None:
    p = MyListingPaginator(client, '')
    assert p.count == 0

    http.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "dist": 2,
        "children": [
            {"name": "a"},
            {"name": "b"}
        ],
        "after": "b",
        "before": "a"
    }
}
'''
    result = await p.__anext__()
    assert len(result) == 2
    assert p.count == 2

    http.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "modhash": null,
        "dist": 3,
        "children": [
            {"name": "c"},
            {"name": "d"},
            {"name": "e"}
        ],
        "after": "e",
        "before": "c"
    }
}
'''
    result = await p.__anext__()
    assert len(result) == 3
    assert p.count == 5

@pytest.mark.asyncio
async def test_cursor() -> None:
    p = MyListingPaginator(client, '')
    assert p.cursor is p.back_cursor is None

    for direction in (True, False):
        p.set_direction(direction)

        p.has_next = True
        p.cursor = None
        p.back_cursor = None
        http.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "dist": 2,
        "children": [
            {"name": "a"},
            {"name": "b"}
        ],
        "after": "b",
        "before": "a"
    }
}
'''
        await p.__anext__()
        assert p.cursor == 'b'
        assert p.back_cursor == 'a'

        p.has_next = True
        p.cursor = None
        p.back_cursor = None
        http.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "dist": 2,
        "children": [
            {"name": "a"},
            {"name": "b"}
        ],
        "after": "b",
        "before": "a"
    }
}
'''
        await p.__anext__()
        assert p.cursor == 'b'
        assert p.back_cursor == 'a'

        p.has_next = True
        p.cursor = None
        p.back_cursor = None
        http.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "dist": 2,
        "children": [
            {"name": "a"},
            {"name": "b"}
        ],
        "after": null,
        "before": "a"
    }
}
'''
        await p.__anext__()
        assert p.cursor == 'b'
        assert p.back_cursor == 'a'

        p.has_next = True
        p.cursor = None
        p.back_cursor = None
        http.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "dist": 2,
        "children": [
            {"name": "a"},
            {"name": "b"}
        ],
        "after": "b",
        "before": null
    }
}
'''
        await p.__anext__()
        assert p.cursor == 'b'
        assert p.back_cursor == 'a'

        p.has_next = True
        p.cursor = None
        p.back_cursor = None
        http.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "dist": 2,
        "children": [
            {"name": "a"},
            {"name": "b"}
        ],
        "after": null,
        "before": null
    }
}
'''
        await p.__anext__()
        assert p.cursor == 'b'
        assert p.back_cursor == 'a'

        p.has_next = True
        p.cursor = None
        p.back_cursor = None
        http.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "dist": 2,
        "children": [
            {"name": "a"}
        ],
        "after": null,
        "before": null
    }
}
'''
        await p.__anext__()
        assert p.cursor == 'a'
        assert p.back_cursor == 'a'

        p.has_next = True
        p.cursor = 'cursor1'
        p.back_cursor = 'cursor2'
        http.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "dist": 0,
        "children": [],
        "after": null,
        "before": null
    }
}
'''
        await p.__anext__()
        assert p.cursor == 'cursor1'
        assert p.back_cursor == 'cursor2'

@pytest.mark.asyncio
async def test_has_next_and_has_prev() -> None:
    p = MyListingPaginator(client, '')
    assert p.has_next is not p.has_prev

    for direction in (True, False):
        p.set_direction(direction)

        p.has_next = True
        p.has_prev = False
        http.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "dist": 0,
        "children": [
            {"name": "a"},
            {"name": "b"}
        ],
        "after": "b",
        "before": "a"
    }
}
'''
        await p.__anext__()
        assert p.has_next and p.has_prev

        p.has_next = True
        p.has_prev = direction
        http.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "dist": 0,
        "children": [
            {"name": "a"},
            {"name": "b"}
        ],
        "after": "b",
        "before": null
    }
}
'''
        await p.__anext__()
        assert p.has_next is direction
        assert p.has_prev is not direction

        p.has_next = True
        p.has_prev = not direction
        http.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "dist": 0,
        "children": [
            {"name": "a"},
            {"name": "b"}
        ],
        "after": null,
        "before": "a"
    }
}
'''
        await p.__anext__()
        assert p.has_next is not direction
        assert p.has_prev is direction

        p.has_next = True
        p.has_prev = direction
        http.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "dist": 0,
        "children": [],
        "after": null,
        "before": null
    }
}
'''
        await p.__anext__()
        assert p.has_next is False
        assert p.has_prev is direction
