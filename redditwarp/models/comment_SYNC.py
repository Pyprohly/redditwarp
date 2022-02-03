
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any, Optional
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .comment_base import (
    BaseComment,
    BaseExtraSubmissionFieldsComment,
    BaseEditPostTextEndpointComment,
)

class Comment(BaseComment):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client: Client = client

    def reply(self, text: str) -> Comment:
        return self.client.p.comment.reply(self.id, text)

    def edit_body(self, text: str) -> EditPostTextEndpointComment:
        return self.client.p.comment.edit_body(self.id, text)

    def delete(self) -> None:
        self.client.p.comment.delete(self.id)

    def lock(self) -> None:
        self.client.p.comment.lock(self.id)

    def unlock(self) -> None:
        self.client.p.comment.unlock(self.id)

    def distinguish(self) -> Comment:
        return self.client.p.comment.distinguish(self.id)

    def distinguish_and_sticky(self) -> Comment:
        return self.client.p.comment.distinguish_and_sticky(self.id)

    def undistinguish(self) -> Comment:
        return self.client.p.comment.undistinguish(self.id)

    def approve(self) -> None:
        self.client.p.comment.approve(self.id)

    def remove(self) -> None:
        self.client.p.comment.remove(self.id)

    def remove_spam(self) -> None:
        self.client.p.comment.remove_spam(self.id)

    def apply_removal_reason(self,
            reason_id: Optional[str],
            note: Optional[str] = None) -> None:
        self.client.p.comment.apply_removal_reason(self.id, reason_id, note)

    def send_removal_comment(self,
            title: str,
            message: str) -> Comment:
        return self.client.p.comment.send_removal_comment(self.id, title, message)

    def send_removal_message(self,
            title: str,
            message: str,
            *,
            exposed: bool = False) -> None:
        self.client.p.comment.send_removal_message(self.id, title, message, exposed=exposed)


class ExtraSubmissionFieldsComment(Comment, BaseExtraSubmissionFieldsComment):
    pass

class EditPostTextEndpointComment(Comment, BaseEditPostTextEndpointComment):
    pass
