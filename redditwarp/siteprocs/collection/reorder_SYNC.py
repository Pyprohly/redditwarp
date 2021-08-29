
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ...util.base_conversion import to_base36

class Reorder:
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, uuid: str, submission_ids: Sequence[int]) -> None:
        submission_id36s = [to_base36(i) for i in submission_ids]
        return self.by_id36(uuid, submission_id36s)

    def by_id36(self, uuid: str, submission_id36s: Sequence[str]) -> None:
        submission_full_id36s = ['t3_' + s for s in submission_id36s]
        link_ids_str = ','.join(submission_full_id36s)
        params = {'collection_id': uuid, 'link_ids': link_ids_str}
        self._client.request('POST', '/api/v1/collections/reorder_collection', params=params)
