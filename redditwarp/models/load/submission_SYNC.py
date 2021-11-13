
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
    if d.get('post_hint') == 'image':
        return ImagePost(d, client)
    if d['is_video']:
        return VideoPost(d, client)
    if d.get('is_gallery', False):
        return GalleryPost(d, client)
    if 'poll_data' in d:
        return PollPost(d, client)
    if 'crosspost_parent' in d:
        return CrosspostPost(d, client)
    if d['is_self']:
        return TextPost(d, client)
    if 'url_overridden_by_dest' in d:
        return LinkPost(d, client)
    raise Exception('unknown post type')
