
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...client_ASYNC import Client

from ...util.base_conversion import to_base36

class AddPost:
    def __init__(self, client: Client):
        self._client = client

    async def __call__(self, uuid: str, submission_id: int) -> None:
        id36 = to_base36(submission_id)
        return await self.by_id36(uuid, id36)

    async def by_id36(self, uuid: str, submission_id36: str) -> None:
        params = {'collection_id': uuid, 'link_fullname': 't3_' + submission_id36}
        await self._client.request('POST', '/api/v1/collections/add_post_to_collection', params=params)
