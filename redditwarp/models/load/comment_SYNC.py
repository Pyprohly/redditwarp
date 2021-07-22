
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ..comment_SYNC import (
    NormalComment,
    ExtraSubmissionFieldsComment,
    EditPostTextEndpointComment,
)

def load_normal_comment(d: Mapping[str, Any], client: Client) -> NormalComment:
    return NormalComment(d, client)

def load_extra_submission_fields_comment(d: Mapping[str, Any], client: Client) -> ExtraSubmissionFieldsComment:
    return ExtraSubmissionFieldsComment(d, client)

def load_edit_post_text_endpoint_comment(d: Mapping[str, Any], client: Client) -> EditPostTextEndpointComment:
    return EditPostTextEndpointComment(d, client)
