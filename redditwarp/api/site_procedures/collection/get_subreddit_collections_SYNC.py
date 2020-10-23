
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
if TYPE_CHECKING:
    from ....client_SYNC import Client
    from ....models.submission_collection_SYNC import SubmissionCollection

from ...load.submission_collection_SYNC import load_submission_collection
from ....util.base_conversion import to_base36

class GetSubredditCollections:
    def __init__(self, client: Client):
        self._client = client

    def __call__(self, id: int) -> Sequence[SubmissionCollection]:
        id36 = to_base36(id)
        return self.by_id36(id36)

    def by_id36(self, id36: str) -> Sequence[SubmissionCollection]:
        params = {'sr_fullname': 't5_' + id36}
        root = self._client.request('GET', '/api/v1/collections/subreddit_collections', params=params)
        return [load_submission_collection(d, self._client) for d in root]
