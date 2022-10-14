
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Optional
if TYPE_CHECKING:
    from ..http.requestor_ASYNC import Requestor
    from ..http.request import Request
    from ..http.response import Response

from urllib.parse import urlsplit

from ..http.requestor_augmenter_ASYNC import RequestorAugmenter

class RedditGiveMeJSONPlease(RequestorAugmenter):
    PARAMS: Mapping[str, str] = {
        'raw_json': '1',
        'api_type': 'json',
    }
    PUBLIC_API_HOST: str = 'oauth.reddit.com'

    def __init__(self, requestor: Requestor) -> None:
        super().__init__(requestor)
        self.params: Mapping[str, str] = dict(self.PARAMS)
        self.public_api_host: str = self.PUBLIC_API_HOST

    async def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        targeting_public_api = urlsplit(request.uri).netloc == self.public_api_host
        if targeting_public_api:
            rp = request.params
            for k, v in self.params.items():
                if rp.setdefault(k, v) == '\0':
                    del rp[k]

        return await self.requestor.send(request, timeout=timeout, follow_redirects=follow_redirects)
