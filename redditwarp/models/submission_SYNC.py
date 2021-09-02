
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .submission_base import (
    BaseSubmission,
    BaseLinkPost,
    BaseTextPost,
    BaseImagePost,
    BaseVideoPost,
    BaseGalleryPost,
    BasePollPost,
    BaseCrosspostPost,
)

class Submission(BaseSubmission):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client = client

class LinkPost(Submission, BaseLinkPost):
    pass

class TextPost(Submission, BaseTextPost):
    pass

class ImagePost(Submission, BaseImagePost):
    pass

class VideoPost(Submission, BaseVideoPost):
    pass

class GalleryPost(Submission, BaseGalleryPost):
    pass

class PollPost(Submission, BasePollPost):
    pass

class CrosspostPost(Submission, BaseCrosspostPost):
    pass
