
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, ClassVar
if TYPE_CHECKING:
    from ..http.handler_ASYNC import Handler
    from ..http.send_params import SendParams
    from ..http.exchange import Exchange

from ..http.delegating_handler_ASYNC import DelegatingHandler

class RedditPleaseSendJSON(DelegatingHandler):
    PARAMS: ClassVar[Mapping[str, str]] = {
        'raw_json': '1',
        'api_type': 'json',
    }

    def __init__(self, handler: Handler) -> None:
        super().__init__(handler)
        self.params: Mapping[str, str] = dict(self.PARAMS)
        ("")

    async def _send(self, p: SendParams) -> Exchange:
        params = p.requisition.params
        for k, v in self.params.items():
            if params.setdefault(k, v) == '\0':
                del params[k]
        return await super()._send(p)
