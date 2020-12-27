
import pytest

from typing import Sequence, Any, Optional, Mapping, Callable
from redditwarp.client_ASYNC import Client
from redditwarp.core.http_client_ASYNC import RedditHTTPClient
from redditwarp.http.base_session_ASYNC import BaseSession
from redditwarp.http.request import Request
from redditwarp.http.response import Response
from redditwarp.http.payload import RequestFiles
from redditwarp.iterators.paginators.listing.listing_async_paginator import ListingAsyncPaginator

class MySession(BaseSession):
    async def send(self, request: Request, *, timeout: float = 0,
            aux_info: Optional[Mapping[Any, Any]] = None) -> Response:
        return Response(0, {}, b'')

class MyHTTPClient(RedditHTTPClient):
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
        headers: Optional[Mapping[str, str]] = None,
        data: Any = None,
        json: Any = None,
        files: Optional[RequestFiles] = None,
        timeout: float = 0,
        aux_info: Optional[Mapping[Any, Any]] = None,
    ) -> Response:
        return Response(self.response_status, self.response_headers, self.response_data)

class MyListingAsyncPaginator(ListingAsyncPaginator[str]):
    def __init__(self,
        client: Client,
        uri: str,
    ):
        cursor_extractor: Callable[[Any], str] = lambda x: x['name']
        super().__init__(client, uri, cursor_extractor=cursor_extractor)

    async def _fetch_result(self) -> Sequence[str]:
        data = await self._fetch_data()
        return [d['name'] for d in data['children']]

http = MyHTTPClient(200, {'Content-Type': 'application/json'}, b'')
client = Client.from_http(http)

@pytest.mark.asyncio
async def test_reset() -> None:
    p = MyListingAsyncPaginator(client, '')
    p.forward_cursor = ''
    p.forward_available = True
    p.backward_cursor = ''
    p.backward_available = True
    p.reset()
    assert p.forward_cursor is None
    assert p.forward_available is None
    assert p.backward_cursor is None
    assert p.backward_available is None

@pytest.mark.asyncio
async def test_resume() -> None:
    p = MyListingAsyncPaginator(client, '')
    p.resuming = False
    p.resume()
    assert p.resuming

@pytest.mark.asyncio
async def test_resuming() -> None:
    p = MyListingAsyncPaginator(client, '')
    p.resume()
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
    assert not p.resuming


@pytest.mark.asyncio
async def test_return_value_and_count() -> None:
    p = MyListingAsyncPaginator(client, '')
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
    p = MyListingAsyncPaginator(client, '')
    assert p.forward_cursor is p.backward_cursor is None

    for direction in (True, False):
        p.set_direction(direction)

        p.reset()
        p.resume()
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
        assert p.forward_cursor == 'b'
        assert p.backward_cursor == 'a'

        p.reset()
        p.resume()
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
        assert p.forward_cursor == 'b'
        assert p.backward_cursor == 'a'

        p.reset()
        p.resume()
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
        assert p.forward_cursor == 'b'
        assert p.backward_cursor == 'a'

        p.reset()
        p.resume()
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
        assert p.forward_cursor == 'b'
        assert p.backward_cursor == 'a'

        p.reset()
        p.resume()
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
        assert p.forward_cursor == 'b'
        assert p.backward_cursor == 'a'

        p.reset()
        p.resume()
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
        assert p.forward_cursor == 'a'
        assert p.backward_cursor == 'a'

        p.reset()
        p.resume()
        p.forward_cursor = 'no_change1'
        p.backward_cursor = 'no_change2'
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
        assert p.forward_cursor == 'no_change1'
        assert p.backward_cursor == 'no_change2'

@pytest.mark.asyncio
async def test_has_next() -> None:
    p = MyListingAsyncPaginator(client, '')

    for direction in (True, False):
        p.set_direction(direction)

        p.reset()
        p.resume()
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
        assert p.has_next()

        p.reset()
        p.resume()
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
        assert p.has_next() is direction

        p.reset()
        p.resume()
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
        assert p.has_next() is not direction

        p.reset()
        p.resume()
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
        assert not p.has_next()
