
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional, Mapping
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ..submission_ASYNC import Submission

from ..submission_ASYNC import TextPost, LinkPost

def load_submission(d: Mapping[str, Any], client: Client) -> Submission:
    if d['is_self']:
        return TextPost(d, client)
    return LinkPost(d, client)

def try_load_linkpost(d: Mapping[str, Any], client: Client) -> Optional[LinkPost]:
    if d['is_self']:
        return None
    return LinkPost(d, client)

def try_load_textpost(d: Mapping[str, Any], client: Client) -> Optional[TextPost]:
    if d['is_self']:
        return TextPost(d, client)
    return None
