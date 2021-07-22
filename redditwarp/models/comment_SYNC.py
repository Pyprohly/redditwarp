
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .mixins.comment import (
    Comment as CommentMixin,
    NormalComment as NormalCommentMixin,
    ExtraSubmissionFieldsComment as ExtraSubmissionFieldsCommentMixin,
    EditPostTextEndpointComment as EditPostTextEndpointCommentMixin,
)

class Comment(CommentMixin):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client = client

class NormalComment(Comment, NormalCommentMixin):
    pass

class ExtraSubmissionFieldsComment(Comment, ExtraSubmissionFieldsCommentMixin):
    pass

class EditPostTextEndpointComment(Comment, EditPostTextEndpointCommentMixin):
    pass
