
from __future__ import annotations

import pytest

from redditwarp.core.reddit_token_obtainment_client_ASYNC import RedditTokenObtainmentClient
from redditwarp.core.exceptions import AuthError
from redditwarp.http.http_client_ASYNC import HTTPClient
from redditwarp.http.handler_ASYNC import Handler
from redditwarp.http.send_params import SendParams
from redditwarp.http.exchange import Exchange
from redditwarp.http.requisition import Requisition
from redditwarp.http.request import Request
from redditwarp.http.response import Response


class MyHandler(Handler):
    DUMMY_REQUISITION = Requisition('', '', {}, {}, None)
    DUMMY_REQUEST = Request('', '', {})

    def __init__(self, response: Response) -> None:
        self.response = response

    async def _send(self, p: SendParams) -> Exchange:
        return Exchange(
            requisition=self.DUMMY_REQUISITION,
            request=self.DUMMY_REQUEST,
            response=self.response,
            history=(),
        )


@pytest.mark.asyncio
async def test_fetch_data_exception() -> None:
    handler = MyHandler(
        Response(
            401,
            {'Content-Type': 'application/json'},
            b'{"message": "Unauthorized", "error": 401}',
        ),
    )
    toc = RedditTokenObtainmentClient(
        HTTPClient(handler),
        '', ('', ''), {},
    )
    with pytest.raises(AuthError):
        await toc.fetch_data()
