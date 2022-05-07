
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ..client_ASYNC import Client

from ..models.comment_ASYNC import (
    Comment,
    ExtraSubmissionFieldsComment,
    EditPostTextEndpointComment,
)

def load_comment(d: Mapping[str, Any], client: Client) -> Comment:
    return Comment(d, client)

def load_extra_submission_fields_comment(d: Mapping[str, Any], client: Client) -> ExtraSubmissionFieldsComment:
    return ExtraSubmissionFieldsComment(d, client)

def load_edit_post_text_endpoint_comment(d: Mapping[str, Any], client: Client) -> EditPostTextEndpointComment:
    return EditPostTextEndpointComment(d, client)
