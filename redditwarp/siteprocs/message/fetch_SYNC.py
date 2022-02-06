
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.message_SYNC import ComposedMessage

from ...models.load.message_SYNC import load_composed_message
from ...util.base_conversion import to_base36

class Fetch:
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, id: int) -> ComposedMessage:
        id36 = to_base36(id)
        return self.by_id36(id36)

    def by_id36(self, id36: str) -> ComposedMessage:
        if not id36:
            raise ValueError('id36 must not be empty')
        root = self._client.request('GET', f'/message/messages/{id36}')
        obj_data = root['data']['children'][0]['data']
        return load_composed_message(obj_data, self._client)
