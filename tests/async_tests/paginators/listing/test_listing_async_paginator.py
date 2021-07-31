
import pytest

from typing import Sequence, Any, Optional, Mapping, Callable
from redditwarp.client_ASYNC import Client
from redditwarp.core.http_client_ASYNC import RedditHTTPClient
from redditwarp.http.session_base_ASYNC import SessionBase
from redditwarp.http.request import Request
from redditwarp.http.response import Response
from redditwarp.http.payload import RequestFiles
from redditwarp.paginators.listing.listing_async_paginator import ListingAsyncPaginator

class MySession(SessionBase):
    async def send(self, request: Request, *, timeout: float = -2,
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
        timeout: float = -2,
        aux_info: Optional[Mapping[Any, Any]] = None,
    ) -> Response:
        return Response(self.response_status, self.response_headers, self.response_data)

class MyListingAsyncPaginator(ListingAsyncPaginator[str]):
    def __init__(self,
        client: Client,
        path: str,
    ):
        cursor_extractor: Callable[[Any], str] = lambda x: x['name']
        super().__init__(client, path, cursor_extractor=cursor_extractor)

    async def _fetch_result(self) -> Sequence[str]:
        data = await self._fetch_data()
        return [d['name'] for d in data['children']]

http = MyHTTPClient(200, {'Content-Type': 'application/json'}, b'')
client = Client.from_http(http)

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
    result = await p.next_result()
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
    result = await p.next_result()
    assert len(result) == 3
    assert p.count == 5

@pytest.mark.asyncio
async def test_cursor_extractor() -> None:
    p = MyListingAsyncPaginator(client, '')

    for direction in (True, False):
        p.direction = direction

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
        await p.next_result()
        assert p.after == 'b'
        assert p.before == 'a'

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
        await p.next_result()
        assert p.after == 'b'
        assert p.before == 'a'

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
        await p.next_result()
        assert p.after == 'b'
        assert p.before == 'a'

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
        await p.next_result()
        assert p.after == 'b'
        assert p.before == 'a'

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
        await p.next_result()
        assert p.after == 'b'
        assert p.before == 'a'

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
        await p.next_result()
        assert p.after == 'a'
        assert p.before == 'a'

        p.after = 'no_change1'
        p.before = 'no_change2'
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
        await p.next_result()
        assert p.after == 'no_change1'
        assert p.before == 'no_change2'

@pytest.mark.asyncio
async def test_next_available() -> None:
    p = MyListingAsyncPaginator(client, '')

    for direction in (True, False):
        p.direction = direction

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
        await p.next_result()
        assert p.next_available()

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
        await p.next_result()
        assert p.next_available() is direction

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
        await p.next_result()
        assert p.next_available() is not direction

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
        await p.next_result()
        assert not p.next_available()

@pytest.mark.asyncio
async def test_dist_none_value() -> None:
    p = MyListingAsyncPaginator(client, '')
    assert p.count == 0

    http.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "dist": null,
        "children": [
            {"name": "a"},
            {"name": "b"}
        ],
        "after": "b",
        "before": "a"
    }
}
'''
    result = await p.next_result()
    assert len(result) == 2
    assert p.count == 2
