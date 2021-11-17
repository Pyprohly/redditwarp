
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .submission_base import (
    BaseSubmission,
    BaseLinkPost,
    BaseTextPost,
    BaseGalleryPost,
    BasePollPost,
    GenericBaseCrosspostSubmission,
)

class Submission(BaseSubmission):
    def __init__(self, d: Mapping[str, Any], client: Client):
        self.client: Client = client
        super().__init__(d)

class LinkPost(Submission, BaseLinkPost):
    pass

class TextPost(Submission, BaseTextPost):
    pass

class GalleryPost(Submission, BaseGalleryPost):
    pass

class PollPost(Submission, BasePollPost):
    pass

class CrosspostSubmission(Submission, GenericBaseCrosspostSubmission[Submission]):
    def _load_submission(self, d: Mapping[str, Any]) -> Submission:
        from .load.submission_SYNC import load_submission
        return load_submission(d, self.client)
