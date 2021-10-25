
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
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

class ExtraSubmissionFieldsComment(Comment, BaseExtraSubmissionFieldsComment):
    pass

class EditPostTextEndpointComment(Comment, BaseEditPostTextEndpointComment):
    pass
