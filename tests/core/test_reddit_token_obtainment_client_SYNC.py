
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from redditwarp.http.request import Request

import pytest

from redditwarp.http.requestor_SYNC import Requestor
from redditwarp.http.response import Response
from redditwarp.core.reddit_token_obtainment_client_SYNC import RedditTokenObtainmentClient
from redditwarp.http.exceptions import StatusCodeException

class MockRequestor(Requestor):
    def __init__(self, response: Response) -> None:
        self.response = response

    def send(self, request: Request, *, timeout: float = -2) -> Response:
        return self.response


def test_StatusCodeException() -> None:
    requestor = MockRequestor(
            Response(401, {'Content-Type': 'application/json'},
                b'{"message": "Unauthorized", "error": 401}'))
    toc = RedditTokenObtainmentClient(
        requestor,
        '', ('cid', 'cse'), {},
        headers={},
    )
    with pytest.raises(StatusCodeException):
        toc.fetch_data()
