
import pytest

from typing import Sequence, Any, MutableMapping, Callable
from redditwarp.client_ASYNC import Client
from redditwarp.core.reddit_http_client_ASYNC import RedditHTTPClient
from redditwarp.core.recorded_ASYNC import Recorded, Last
from redditwarp.http.session_base_ASYNC import SessionBase
from redditwarp.http.request import Request
from redditwarp.http.response import Response
from redditwarp.pagination.listing.listing_async_paginator import ListingAsyncPaginator

class MySession(SessionBase):
    def __init__(self,
        response_status: int,
        response_headers: MutableMapping[str, str],
        response_data: bytes,
    ) -> None:
        super().__init__()
        self.response_status = response_status
        self.response_headers = response_headers
        self.response_data = response_data

    async def send(self, request: Request, *, timeout: float = -2) -> Response:
        return Response(self.response_status, self.response_headers, self.response_data)

class MyListingAsyncPaginator(ListingAsyncPaginator[str]):
    def __init__(self,
        client: Client,
        uri: str,
    ):
        cursor_extractor: Callable[[Any], str] = lambda x: x['name']
        super().__init__(client, uri, cursor_extractor=cursor_extractor)

    async def fetch(self) -> Sequence[str]:
        data = await self._fetch_data()
        return [d['name'] for d in data['children']]

session = MySession(200, {'Content-Type': 'application/json'}, b'')
recorder = Recorded(session)
last = Last(recorder)
http = RedditHTTPClient(session=session, requestor=recorder, last=last)
client = Client.from_http(http)

@pytest.mark.asyncio
async def test_none_limit() -> None:
    p = MyListingAsyncPaginator(client, '')
    session.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "dist": 0,
        "children": [],
        "after": "a",
        "before": "b"
    }
}
'''
    p.limit = None
    await p.fetch()

    req = http.last.request
    assert req is not None

    assert 'limit' not in req.params

    p.limit = 14
    await p.fetch()

    req = http.last.request
    assert req is not None

    assert req.params['limit'] == '14'

@pytest.mark.asyncio
async def test_dont_send_empty_cursor() -> None:
    p = MyListingAsyncPaginator(client, '')
    session.response_data = b'''\
{
    "kind": "Listing",
    "data": {
        "dist": 0,
        "children": [],
        "after": "a",
        "before": "b"
    }
}
'''
    p.limit = None
    await p.fetch()

    req = http.last.request
    assert req is not None

    assert 'after' not in req.params

@pytest.mark.asyncio
async def test_return_value_and_count() -> None:
    p = MyListingAsyncPaginator(client, '')
    assert p.after_count == 0

    session.response_data = b'''\
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
    result = await p.fetch()
    assert len(result) == 2
    assert p.after_count == 2

    session.response_data = b'''\
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
    result = await p.fetch()
    assert len(result) == 3
    assert p.after_count == 5

@pytest.mark.asyncio
async def test_cursor_extractor() -> None:
    p = MyListingAsyncPaginator(client, '')

    for direction in (True, False):
        p.direction = direction

        session.response_data = b'''\
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
        await p.fetch()
        assert p.after == 'b'
        assert p.before == 'a'

        session.response_data = b'''\
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
        await p.fetch()
        assert p.after == 'b'
        assert p.before == 'a'

        session.response_data = b'''\
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
        await p.fetch()
        assert p.after == 'b'
        assert p.before == 'a'

        session.response_data = b'''\
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
        await p.fetch()
        assert p.after == 'b'
        assert p.before == 'a'

        session.response_data = b'''\
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
        await p.fetch()
        assert p.after == 'b'
        assert p.before == 'a'

        session.response_data = b'''\
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
        await p.fetch()
        assert p.after == 'a'
        assert p.before == 'a'

        p.after = 'no_change1'
        p.before = 'no_change2'
        session.response_data = b'''\
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
        await p.fetch()
        assert p.after == 'no_change1'
        assert p.before == 'no_change2'

@pytest.mark.asyncio
async def test_more_available() -> None:
    p = MyListingAsyncPaginator(client, '')

    for direction in (True, False):
        p.direction = direction

        session.response_data = b'''\
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
        await p.fetch()
        assert p.more_available()

        session.response_data = b'''\
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
        await p.fetch()
        assert p.more_available() is direction

        session.response_data = b'''\
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
        await p.fetch()
        assert p.more_available() is not direction

        session.response_data = b'''\
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
        await p.fetch()
        assert not p.more_available()

@pytest.mark.asyncio
async def test_dist_none_value() -> None:
    p = MyListingAsyncPaginator(client, '')
    assert p.after_count == 0

    session.response_data = b'''\
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
    result = await p.fetch()
    assert len(result) == 2
    assert p.after_count == 2
