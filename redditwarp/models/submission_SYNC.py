
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .mixins.submission import (
    Submission as SubmissionMixin,
    LinkPost as LinkPostMixin,
    TextPost as TextPostMixin,
    ImagePost as ImagePostMixin,
    VideoPost as VideoPostMixin,
    GalleryPost as GalleryPostMixin,
    PollPost as PollPostMixin,
    CrosspostPost as CrosspostPostMixin,
)

class Submission(SubmissionMixin):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client = client

class LinkPost(Submission, LinkPostMixin):
    pass

class TextPost(Submission, TextPostMixin):
    pass

class ImagePost(Submission, ImagePostMixin):
    pass

class VideoPost(Submission, VideoPostMixin):
    pass

class GalleryPost(Submission, GalleryPostMixin):
    pass

class PollPost(Submission, PollPostMixin):
    pass

class CrosspostPost(Submission, CrosspostPostMixin):
    pass
