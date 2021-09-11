
from __future__ import annotations

import pytest

from redditwarp.auth.reddit_token_obtainment_client_SYNC import RedditTokenObtainmentClient
from redditwarp.auth.exceptions import HTTPStatusError

from .test_token_obtainment_client_SYNC import MockRequestor

def test_fetch_json_dict__exceptions() -> None:
    requestor = MockRequestor(
        response_status=401,
        response_headers={'Content-Type': 'application/json'},
        response_data=b'{"message": "Unauthorized", "error": 401}',
    )
    o = RedditTokenObtainmentClient(
        requestor,
        '', ('cid', 'cse'), {},
        {},
    )
    with pytest.raises(HTTPStatusError):
        o.fetch_json_dict()