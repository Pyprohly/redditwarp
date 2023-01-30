
from typing import Sequence, Any, MutableMapping, Callable
from redditwarp.client_SYNC import Client
from redditwarp.core.http_client_SYNC import HTTPClient
from redditwarp.http.handler_SYNC import Handler
from redditwarp.http.send_params import SendParams
from redditwarp.http.exchange import Exchange
from redditwarp.http.requisition import Requisition
from redditwarp.http.request import Request
from redditwarp.http.response import Response
from redditwarp.pagination.paginators.listing.listing_paginator import ListingPaginator


class MyHandler(Handler):
    DUMMY_REQUISITION = Requisition('', '', {}, {}, None)
    DUMMY_REQUEST = Request('', '', {}, b'')

    def __init__(self,
        response_status: int,
        response_headers: MutableMapping[str, str],
        response_data: bytes,
    ) -> None:
        super().__init__()
        self.response_status = response_status
        self.response_headers = response_headers
        self.response_data = response_data

    def _send(self, p: SendParams) -> Exchange:
        resp = Response(self.response_status, self.response_headers, self.response_data)
        return Exchange(
            requisition=self.DUMMY_REQUISITION,
            request=self.DUMMY_REQUEST,
            response=resp,
            history=(),
        )


class MyListingPaginator(ListingPaginator[str]):
    def __init__(self,
        client: Client,
        url: str,
    ) -> None:
        cursor_extractor: Callable[[Any], str] = lambda x: x['name']
        super().__init__(client, url, cursor_extractor=cursor_extractor)

    def fetch(self) -> Sequence[str]:
        data = self._fetch_data()
        return [d['name'] for d in data['children']]


handler = MyHandler(200, {'Content-Type': 'application/json'}, b'')
http = HTTPClient(handler)
client = Client.from_http(http)

def test_none_limit() -> None:
    p = MyListingPaginator(client, '')
    handler.response_data = b'''\
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
    p.fetch()

    req = http.last.requisition
    assert req is not None

    assert 'limit' not in req.params

    p.limit = 14
    p.fetch()

    req = http.last.requisition
    assert req is not None

    assert req.params['limit'] == '14'

def test_dont_send_empty_cursor() -> None:
    p = MyListingPaginator(client, '')
    handler.response_data = b'''\
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
    p.fetch()

    req = http.last.requisition
    assert req is not None

    assert 'after' not in req.params

def test_return_value_and_count() -> None:
    p = MyListingPaginator(client, '')
    assert p.after_count == 0

    handler.response_data = b'''\
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
    result = p.fetch()
    assert len(result) == 2
    assert p.after_count == 2

    handler.response_data = b'''\
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
    result = p.fetch()
    assert len(result) == 3
    assert p.after_count == 5

def test_cursor_extractor() -> None:
    p = MyListingPaginator(client, '')

    for direction in (True, False):
        p.direction = direction

        handler.response_data = b'''\
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
        p.fetch()
        assert p.after == 'b'
        assert p.before == 'a'

        handler.response_data = b'''\
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
        p.fetch()
        assert p.after == 'b'
        assert p.before == 'a'

        handler.response_data = b'''\
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
        p.fetch()
        assert p.after == 'b'
        assert p.before == 'a'

        handler.response_data = b'''\
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
        p.fetch()
        assert p.after == 'b'
        assert p.before == 'a'

        handler.response_data = b'''\
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
        p.fetch()
        assert p.after == 'b'
        assert p.before == 'a'

        handler.response_data = b'''\
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
        p.fetch()
        assert p.after == 'a'
        assert p.before == 'a'

        p.after = 'no_change1'
        p.before = 'no_change2'
        handler.response_data = b'''\
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
        p.fetch()
        assert p.after == 'no_change1'
        assert p.before == 'no_change2'

def test_has_more() -> None:
    p = MyListingPaginator(client, '')

    for direction in (True, False):
        p.direction = direction

        handler.response_data = b'''\
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
        p.fetch()
        assert p.has_more()

        handler.response_data = b'''\
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
        p.fetch()
        assert p.has_more() is direction

        handler.response_data = b'''\
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
        p.fetch()
        assert p.has_more() is not direction

        handler.response_data = b'''\
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
        p.fetch()
        assert not p.has_more()

def test_dist_none_value() -> None:
    # Example endpoints where `dist`is null:
    #   GET /message/messages
    #   GET /live/{thread_id}

    p = MyListingPaginator(client, '')
    assert p.after_count == 0

    handler.response_data = b'''\
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
    result = p.fetch()
    assert len(result) == 2
    assert p.after_count == 2
