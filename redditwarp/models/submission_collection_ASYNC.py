
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any, Sequence
if TYPE_CHECKING:
    from ..client_ASYNC import Client

from .submission_collection_base import (
    SubmissionCollectionDetailsMixinBase,
    SubmissionCollectionMixinBase,
    GenericSubmissionCollectionMixinBase,
)
from .submission_ASYNC import Submission
from .load.submission_ASYNC import load_submission

class SubmissionCollectionDetails(SubmissionCollectionDetailsMixinBase):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client = client

class SubmissionCollection(
    SubmissionCollectionDetails,
    SubmissionCollectionMixinBase,
    GenericSubmissionCollectionMixinBase[Submission],
):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d, client)
        children_data = d['sorted_links']['data']['children']
        subms = [load_submission(i['data'], self.client) for i in children_data]
        self.submissions: Sequence[Submission] = subms
