
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ....client_SYNC import Client

from ...load.partial_user import load_partial_user
from ....models.partial_user import PartialUser
from ....util.base_conversion import to_base36
from .... import exceptions

class FetchPartial:
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, id: int) -> Optional[PartialUser]:
        return self.by_id(id)

    def by_id(self, id: int) -> Optional[PartialUser]:
        id36 = to_base36(id)
        return self.by_id36(id36)

    def by_id36(self, id36: str) -> Optional[PartialUser]:
        full_id36 = 't2_' + id36
        try:
            root = self._client.request('GET', '/api/user_data_by_account_ids',
                    params={'ids': full_id36})
        except exceptions.HTTPStatusError as e:
            if e.response.status == 404:
                return None
            raise
        obj_data = root[full_id36]
        return load_partial_user(obj_data, id36)
