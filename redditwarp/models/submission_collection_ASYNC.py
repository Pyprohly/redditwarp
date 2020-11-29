
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any, Optional, Sequence
if TYPE_CHECKING:
    from ..client_ASYNC import Client
    from .submission_ASYNC import Submission

from .submission_collection_base import (
    SubmissionCollectionBase,
    PrimarySubmissionCollectionBase,
)
from ..api.load.submission_ASYNC import load_submission


class SubmissionCollection(SubmissionCollectionBase):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client = client

class PrimarySubmissionCollection(SubmissionCollection, PrimarySubmissionCollectionBase):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d, client)
        self.submissions: Optional[Sequence[Submission]] = None
        if 'sorted_links' in d:
            children_data = d['sorted_links']['data']['children']
            self.submissions = [load_submission(i['data'], self.client) for i in children_data]
