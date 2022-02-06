
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.message_SYNC import ComposedMessage
    from .SYNC import MessageProcedures

from ...util.base_conversion import to_base36
from ... import http

class Get:
    def __init__(self, outer: MessageProcedures, client: Client):
        self._outer = outer
        self._client = client

    def __call__(self, id: int) -> Optional[ComposedMessage]:
        id36 = to_base36(id)
        return self.by_id36(id36)

    def by_id36(self, id36: str) -> Optional[ComposedMessage]:
        try:
            return self._outer.fetch.by_id36(id36)
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 403:
                return None
            raise
