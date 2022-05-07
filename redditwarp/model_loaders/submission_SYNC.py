
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ..client_SYNC import Client
    from ..models.submission_SYNC import Submission

from ..models.submission_SYNC import (
    LinkPost,
    TextPost,
    GalleryPost,
    PollPost,
    CrosspostSubmission,
)

def load_submission(d: Mapping[str, Any], client: Client) -> Submission:
    if d.get('is_gallery', False):
        return load_gallery_post(d, client)
    if 'poll_data' in d:
        return load_poll_post(d, client)
    if 'crosspost_parent' in d:
        return load_crosspost_submission(d, client)
    if d['is_self']:
        return load_text_post(d, client)
    if 'url_overridden_by_dest' in d:
        return load_link_post(d, client)
    raise Exception('unknown post type')


def load_text_post(d: Mapping[str, Any], client: Client) -> TextPost:
    return TextPost(d, client)

def load_link_post(d: Mapping[str, Any], client: Client) -> LinkPost:
    return LinkPost(d, client)

def load_gallery_post(d: Mapping[str, Any], client: Client) -> GalleryPost:
    return GalleryPost(d, client)

def load_poll_post(d: Mapping[str, Any], client: Client) -> PollPost:
    return PollPost(d, client)

def load_crosspost_submission(d: Mapping[str, Any], client: Client) -> CrosspostSubmission:
    return CrosspostSubmission(d, client)
