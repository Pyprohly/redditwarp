
from typing import Sequence, Any, MutableMapping, Callable
from redditwarp.client_SYNC import Client
from redditwarp.core.reddit_http_client_SYNC import RedditHTTPClient
from redditwarp.core.recorded_SYNC import Recorded, Last
from redditwarp.http.session_base_SYNC import SessionBase
from redditwarp.http.request import Request
from redditwarp.http.response import Response
from redditwarp.paginators.implementations.listing.listing_paginator import ListingPaginator

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

    def send(self, request: Request, *, timeout: float = -2) -> Response:
        return Response(self.response_status, self.response_headers, self.response_data)

class MyListingPaginator(ListingPaginator[str]):
    def __init__(self,
        client: Client,
        uri: str,
    ):
        cursor_extractor: Callable[[Any], str] = lambda x: x['name']
        super().__init__(client, uri, cursor_extractor=cursor_extractor)

    def next_result(self) -> Sequence[str]:
        data = self._next_data()
        return [d['name'] for d in data['children']]

session = MySession(200, {'Content-Type': 'application/json'}, b'')
recorder = Recorded(session)
last = Last(recorder)
http = RedditHTTPClient(session=session, requestor=recorder, last=last)
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

    req = http.last.request
    assert req is not None

    assert 'limit' not in req.params

    p.limit = 14
    p.next_result()

    req = http.last.request
    assert req is not None

    assert req.params['limit'] == '14'

def test_dont_send_empty_cursor() -> None:
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

    req = http.last.request
    assert req is not None

    assert 'after' not in req.params

def test_return_value_and_count() -> None:
    p = MyListingPaginator(client, '')
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
    result = p.next_result()
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
    result = p.next_result()
    assert len(result) == 3
    assert p.after_count == 5

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
    result = p.next_result()
    assert len(result) == 2
    assert p.after_count == 2
