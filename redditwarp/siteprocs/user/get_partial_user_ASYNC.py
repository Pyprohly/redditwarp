
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client

from ...models.partial_user import PartialUser
from ...models.load.partial_user import load_partial_user
from ...util.base_conversion import to_base36
from ... import http

class GetPartialUser:
    def __init__(self, client: Client):
        self._client = client

    async def __call__(self, id: int) -> Optional[PartialUser]:
        return await self.by_id(id)

    async def by_id(self, id: int) -> Optional[PartialUser]:
        id36 = to_base36(id)
        return await self.by_id36(id36)

    async def by_id36(self, id36: str) -> Optional[PartialUser]:
        full_id36 = 't2_' + id36
        try:
            root = await self._client.request('GET', '/api/user_data_by_account_ids',
                    params={'ids': full_id36})
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 404:
                return None
            raise
        obj_data = root[full_id36]
        return load_partial_user(obj_data, id36)
