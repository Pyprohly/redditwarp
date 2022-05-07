
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ...models.user_summary import UserSummary
from ...model_loaders.user_summary import load_user_summary
from ...util.base_conversion import to_base36
from ... import http

class GetUserSummary:
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, id: int) -> Optional[UserSummary]:
        id36 = to_base36(id)
        return self.by_id36(id36)

    def by_id36(self, id36: str) -> Optional[UserSummary]:
        full_id36 = 't2_' + id36
        try:
            root = self._client.request('GET', '/api/user_data_by_account_ids',
                    params={'ids': full_id36})
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 404:
                return None
            raise
        obj_data = root[full_id36]
        return load_user_summary(obj_data, id36)
