
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.user_SYNC import User as UserModel

from .get_partial_user_SYNC import GetPartialUser
from .bulk_fetch_partial_user_SYNC import BulkFetchPartialUser
from .pull_SYNC import Pull
from ...models.load.user_SYNC import load_user
from ... import exceptions

class User:
    def __init__(self, client: Client):
        self._client = client
        self.get_partial_user = GetPartialUser(client)
        self.bulk_fetch_partial_user = BulkFetchPartialUser(client)
        self.pull = Pull(client)

    def get_by_name(self, name: str) -> Optional[UserModel]:
        try:
            root = self._client.request('GET', f'/user/{name}/about')
        except exceptions.HTTPStatusError as e:
            if e.response.status == 404:
                return None
            raise
        return load_user(root['data'], self._client)
