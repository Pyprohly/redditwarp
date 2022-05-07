
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_collection_SYNC import SubmissionCollection

from ...model_loaders.submission_collection_SYNC import load_submission_collection
from ...util.base_conversion import to_base36

class Create:
    def __init__(self, client: Client):
        self._client = client

    def __call__(self,
        sr_id: int,
        title: str,
        description: Optional[str] = None,
        display_layout: Optional[str] = None,
    ) -> SubmissionCollection:
        sr_id36 = to_base36(sr_id)
        return self.by_id36(sr_id36, title, description, display_layout)

    def by_id36(self,
        sr_id36: str,
        title: str,
        description: Optional[str] = None,
        display_layout: Optional[str] = None,
    ) -> SubmissionCollection:
        params = {'sr_fullname': 't5_' + sr_id36, 'title': title}
        if description is not None:
            params['description'] = description
        if display_layout is not None:
            params['display_layout'] = display_layout
        data = self._client.request('POST', '/api/v1/collections/create_collection', params=params)
        return load_submission_collection(data, self._client)
