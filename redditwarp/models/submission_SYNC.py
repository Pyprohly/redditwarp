
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any, Optional
if TYPE_CHECKING:
    from ..client_SYNC import Client
    from .comment_SYNC import Comment

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
        self.client: Client = client  # Must assign client before super call
        super().__init__(d)

    def reply(self, text: str) -> Comment:
        return self.client.p.submission.reply(self.id, text)

    def edit_post_text(self, text: str) -> Submission:
        return self.client.p.submission.edit_post_text(self.id, text)

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
    pass

class GalleryPost(Submission, BaseGalleryPost):
    pass

class PollPost(Submission, BasePollPost):
    pass

class CrosspostSubmission(Submission, GenericBaseCrosspostSubmission[Submission]):
    def _load_submission(self, d: Mapping[str, Any]) -> Submission:
        from .load.submission_SYNC import load_submission  # Cyclic import
        return load_submission(d, self.client)
