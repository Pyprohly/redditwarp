
from typing import Sequence, Any, Mapping, Callable
from redditwarp.client_SYNC import Client
from redditwarp.core.reddit_http_client_SYNC import RedditHTTPClient
from redditwarp.http.session_base_SYNC import SessionBase
from redditwarp.http.request import Request
from redditwarp.http.response import Response
from redditwarp.paginators.implementations.listing.listing_paginator import ListingPaginator

class MySession(SessionBase):
    def __init__(self,
        response_status: int,
        response_headers: Mapping[str, str],
        response_data: bytes,
    ) -> None:
        super().__init__()
        self.response_status = response_status
        self.response_headers = response_headers
        self.response_data = response_data

    def send(self, request: Request, *, timeout: float = -2) -> Response:
        return Response(self.response_status, self.response_headers, self.response_data, request=request)

class MyListingPaginator(ListingPaginator[str]):
    def __init__(self,
        client: Client,
        uri: str,
    ):
        cursor_extractor: Callable[[Any], str] = lambda x: x['name']
        super().__init__(client, uri, cursor_extractor=cursor_extractor)

    def next_result(self) -> Sequence[str]:
        data = self._fetch_data()
        return [d['name'] for d in data['children']]

session = MySession(200, {'Content-Type': 'application/json'}, b'')
http = RedditHTTPClient(session)
client = Client.from_http(http)

def test_none_limit() -> None:
    p = MyListingPaginator(client, '')
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
    p.next_result()

    if http.last_response is None:
        raise Exception
    response = http.last_response
    if response.request is None:
        raise Exception
    request = response.request

    assert 'limit' not in request.params

    p.limit = 14
    p.next_result()

    if http.last_response is None:
        raise Exception
    response = http.last_response
    if response.request is None:
        raise Exception
    request = response.request

    assert request.params['limit'] == '14'

def test_return_value_and_count() -> None:
    p = MyListingPaginator(client, '')
    assert p.count == 0

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
    result = p.next_result()
    assert len(result) == 2
    assert p.count == 2

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
    result = p.next_result()
    assert len(result) == 3
    assert p.count == 5

def test_cursor_extractor() -> None:
    p = MyListingPaginator(client, '')

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
        p.next_result()
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
        p.next_result()
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
        p.next_result()
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
        p.next_result()
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
        p.next_result()
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
        p.next_result()
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
        p.next_result()
        assert p.after == 'no_change1'
        assert p.before == 'no_change2'

def test_next_available() -> None:
    p = MyListingPaginator(client, '')

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
        p.next_result()
        assert p.next_available()

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
        p.next_result()
        assert p.next_available() is direction

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
        p.next_result()
        assert p.next_available() is not direction

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
        p.next_result()
        assert not p.next_available()

def test_dist_none_value() -> None:
    # Example endpoints where `dist`is null:
    #   GET /message/messages
    #   GET /live/{thread_id}

    p = MyListingPaginator(client, '')
    assert p.count == 0

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
    result = p.next_result()
    assert len(result) == 2
    assert p.count == 2
