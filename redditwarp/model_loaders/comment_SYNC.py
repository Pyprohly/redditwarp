
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ..client_SYNC import Client

from ..models.comment_SYNC import (
    Comment,
    LooseComment,
)

def load_comment(d: Mapping[str, Any], client: Client) -> Comment:
    return Comment(d, client)

def load_loose_comment(d: Mapping[str, Any], client: Client) -> LooseComment:
    return LooseComment(d, client)
