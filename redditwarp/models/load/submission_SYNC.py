
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ..submission_SYNC import Submission

from ..submission_SYNC import (
    LinkPost,
    TextPost,
    ImagePost,
    VideoPost,
    GalleryPost,
    PollPost,
    CrosspostPost,
)

def load_submission(d: Mapping[str, Any], client: Client) -> Submission:
    if d['is_self']:
        return TextPost(d, client)
    elif d.get('post_hint') == 'image':
        return ImagePost(d, client)
    elif d['is_video']:
        return VideoPost(d, client)
    elif d.get('is_gallery', False):
        return GalleryPost(d, client)
    elif 'poll_data' in d:
        return PollPost(d, client)
    elif 'crosspost_parent' in d:
        return CrosspostPost(d, client)
    return LinkPost(d, client)
