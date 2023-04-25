
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ..models.submission import Submission

from ..models.submission import (
    LinkPost,
    TextPost,
    GalleryPost,
    PollPost,
    CrosspostSubmission,
)

def load_submission(d: Mapping[str, Any]) -> Submission:
    if d.get('is_gallery', False):
        return load_gallery_post(d)
    if 'poll_data' in d:
        return load_poll_post(d)
    if 'crosspost_parent' in d:
        return load_cross_post(d)
    if d['is_self']:
        return load_text_post(d)
    if 'url_overridden_by_dest' in d:
        return load_link_post(d)
    raise Exception('unknown post type')


def load_link_post(d: Mapping[str, Any]) -> LinkPost:
    return LinkPost(d)

def load_text_post(d: Mapping[str, Any]) -> TextPost:
    return TextPost(d)

def load_gallery_post(d: Mapping[str, Any]) -> GalleryPost:
    return GalleryPost(d)

def load_poll_post(d: Mapping[str, Any]) -> PollPost:
    return PollPost(d)

def load_crosspost_submission(d: Mapping[str, Any]) -> CrosspostSubmission:
    return CrosspostSubmission(d)

def load_cross_post(d: Mapping[str, Any]) -> CrosspostSubmission:
    return load_crosspost_submission(d)
