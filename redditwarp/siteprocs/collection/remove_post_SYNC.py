
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ...util.base_conversion import to_base36

class RemovePost:
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, uuid: str, submission_id: int) -> None:
        id36 = to_base36(submission_id)
        return self.by_id36(uuid, id36)

    def by_id36(self, uuid: str, submission_id36: str) -> None:
        params = {'collection_id': uuid, 'link_fullname': 't5_' + submission_id36}
        self._client.request('POST', '/api/v1/collections/remove_post_in_collection', params=params)
