
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any, Optional
if TYPE_CHECKING:
    from ..client_SYNC import Client
    from .comment_SYNC import Comment

from .submission import (
    Submission as BaseSubmission,
    LinkPost as BaseLinkPost,
    TextPost as BaseTextPost,
    GalleryPost as BaseGalleryPost,
    PollPost as BasePollPost,
    CrosspostSubmission as BaseCrosspostSubmission,
)

class Submission(BaseSubmission):
    def __init__(self, d: Mapping[str, Any], client: Client) -> None:
        super().__init__(d)
        self.client: Client = client

    def reply(self, text: str) -> Comment:
        return self.client.p.submission.reply(self.id, text)

    def delete(self) -> None:
        self.client.p.submission.delete(self.id)

    def lock(self) -> None:
        self.client.p.submission.lock(self.id)

    def unlock(self) -> None:
        self.client.p.submission.unlock(self.id)

    def distinguish(self) -> Submission:
        return self.client.p.submission.distinguish(self.id)

    def undistinguish(self) -> Submission:
        return self.client.p.submission.undistinguish(self.id)

    def sticky(self, slot: Optional[int] = None) -> None:
        self.client.p.submission.sticky(self.id, slot)

    def unsticky(self) -> None:
        self.client.p.submission.unsticky(self.id)

    def approve(self) -> None:
        self.client.p.submission.approve(self.id)

    def remove(self) -> None:
        self.client.p.submission.remove(self.id)

    def apply_removal_reason(self,
            reason_id: Optional[str],
            note: Optional[str] = None) -> None:
        self.client.p.submission.apply_removal_reason(self.id, reason_id, note)

    def send_removal_comment(self,
            title: str,
            message: str) -> Comment:
        return self.client.p.submission.send_removal_comment(self.id, title, message)

    def send_removal_message(self,
            title: str,
            message: str,
            *,
            exposed: bool = False) -> None:
        self.client.p.submission.send_removal_message(self.id, title, message, exposed=exposed)


class LinkPost(Submission, BaseLinkPost):
    pass

class TextPost(Submission, BaseTextPost):
    def edit_body(self, text: str) -> TextPost:
        return self.client.p.submission.edit_text_post_body(self.id, text)

class GalleryPost(Submission, BaseGalleryPost):
    pass

class PollPost(Submission, BasePollPost):
    pass

class CrosspostSubmission(Submission, BaseCrosspostSubmission):
    @property
    def original(self) -> Optional[Submission]:
        return self.__original

    def __init__(self, d: Mapping[str, Any], client: Client) -> None:
        super().__init__(d, client)
        from ..model_loaders.submission_SYNC import load_submission  # Avoid cyclic import
        load = lambda d: load_submission(d, client)
        self.__original: Optional[Submission] = self._load_original(d, load)
