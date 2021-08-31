
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .submission_base import (
    SubmissionMixinBase,
    LinkPostMixinBase,
    TextPostMixinBase,
    ImagePostMixinBase,
    VideoPostMixinBase,
    GalleryPostMixinBase,
    PollPostMixinBase,
    CrosspostPostMixinBase,
)

class Submission(SubmissionMixinBase):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client = client

class LinkPost(Submission, LinkPostMixinBase):
    pass

class TextPost(Submission, TextPostMixinBase):
    pass

class ImagePost(Submission, ImagePostMixinBase):
    pass

class VideoPost(Submission, VideoPostMixinBase):
    pass

class GalleryPost(Submission, GalleryPostMixinBase):
    pass

class PollPost(Submission, PollPostMixinBase):
    pass

class CrosspostPost(Submission, CrosspostPostMixinBase):
    pass
