
from __future__ import annotations
from typing import Any, Mapping, Optional

from datetime import datetime, timezone

from ..models.submission_draft import (
    SubmissionDraft,
    MarkdownTextPostDraft,
    RichTextTextPostDraft,
    LinkPostDraft,
)


normal_to_public_draft_field_names_map: Mapping[str, str] = {
    'id': 'id',
    'kind': 'kind',
    'created': 'created',
    'modified': 'modified',
    'is_public_link': 'isPublicLink',
    'subreddit': 'subredditId',
    'title': 'title',
    'body': 'body',
    'send_replies': 'sendReplies',
    'spoiler': 'isSpoiler',
    'nsfw': 'isNSFW',
    'original_content': 'isOriginalContent',
    'flair': 'flair',
}
normal_draft_field_names_map: Mapping[str, str] = {k: k for k, _ in normal_to_public_draft_field_names_map.items()}
public_draft_field_names_map: Mapping[str, str] = normal_to_public_draft_field_names_map


def _xload_submission_draft_impl(d: Mapping[str, Any], h: Mapping[str, str]) -> SubmissionDraft:
    created_ts: float = d[h['created']] / 1000
    modified_ts: float = d[h['modified']] / 1000

    subreddit_id: Optional[int] = None
    subreddit: Optional[str] = d[h['subreddit']]
    if subreddit is not None:
        _, _, id36 = subreddit.partition('_')
        subreddit_id = int(id36, 36)

    flair: Optional[SubmissionDraft.Flair] = None
    if df := d[h['flair']]:
        flair = SubmissionDraft.Flair(
            uuid=df['templateId'],
            text_mode=df['type'],
            text=df['text'],
            bg_color=df['backgroundColor'],
            fg_color_scheme=df['textColor'],
        )

    return SubmissionDraft(
        d=d,
        uuid=d[h['id']],
        created_at=datetime.fromtimestamp(created_ts, timezone.utc),
        modified_at=datetime.fromtimestamp(modified_ts, timezone.utc),
        public=d[h['is_public_link']],
        subreddit_id=subreddit_id,
        title=d[h['title']],
        reply_notifications=d[h['send_replies']],
        spoiler=d[h['spoiler']],
        nsfw=d[h['nsfw']],
        oc=d[h['original_content']],
        flair=flair,
    )


def _load_markdown_text_post_draft_impl(d: Mapping[str, Any], h: Mapping[str, str]) -> MarkdownTextPostDraft:
    up = _xload_submission_draft_impl(d, h)
    return MarkdownTextPostDraft(
        d=up.d,
        uuid=up.uuid,
        created_at=up.created_at,
        modified_at=up.modified_at,
        public=up.public,
        subreddit_id=up.subreddit_id,
        title=up.title,
        reply_notifications=up.reply_notifications,
        spoiler=up.spoiler,
        nsfw=up.nsfw,
        oc=up.oc,
        flair=up.flair,
        body=d['body'],
    )

def _load_richtext_text_post_draft_impl(d: Mapping[str, Any], h: Mapping[str, str]) -> RichTextTextPostDraft:
    up = _xload_submission_draft_impl(d, h)
    return RichTextTextPostDraft(
        d=up.d,
        uuid=up.uuid,
        created_at=up.created_at,
        modified_at=up.modified_at,
        public=up.public,
        subreddit_id=up.subreddit_id,
        title=up.title,
        reply_notifications=up.reply_notifications,
        spoiler=up.spoiler,
        nsfw=up.nsfw,
        oc=up.oc,
        flair=up.flair,
    )

def _load_link_post_draft_impl(d: Mapping[str, Any], h: Mapping[str, str]) -> LinkPostDraft:
    up = _xload_submission_draft_impl(d, h)
    return LinkPostDraft(
        d=up.d,
        uuid=up.uuid,
        created_at=up.created_at,
        modified_at=up.modified_at,
        public=up.public,
        subreddit_id=up.subreddit_id,
        title=up.title,
        reply_notifications=up.reply_notifications,
        spoiler=up.spoiler,
        nsfw=up.nsfw,
        oc=up.oc,
        flair=up.flair,
        link=d['body'],
    )


def _load_submission_draft_impl(d: Mapping[str, Any], h: Mapping[str, str]) -> SubmissionDraft:
    kind: str = d[h['kind']]
    if kind == 'markdown':
        return _load_markdown_text_post_draft_impl(d, h)
    if kind == 'richtext':
        return _load_richtext_text_post_draft_impl(d, h)
    if kind == 'link':
        return _load_link_post_draft_impl(d, h)
    raise ValueError('unknown draft type')



def load_submission_draft(d: Mapping[str, Any]) -> SubmissionDraft:
    return _load_submission_draft_impl(d, normal_draft_field_names_map)

def load_markdown_text_post_draft(d: Mapping[str, Any]) -> MarkdownTextPostDraft:
    return _load_markdown_text_post_draft_impl(d, normal_draft_field_names_map)

def load_richtext_text_post_draft(d: Mapping[str, Any]) -> RichTextTextPostDraft:
    return _load_richtext_text_post_draft_impl(d, normal_draft_field_names_map)

def load_link_post_draft(d: Mapping[str, Any]) -> LinkPostDraft:
    return _load_link_post_draft_impl(d, normal_draft_field_names_map)


def load_public_submission_draft(d: Mapping[str, Any]) -> SubmissionDraft:
    return _load_submission_draft_impl(d, public_draft_field_names_map)

def load_public_markdown_text_post_draft(d: Mapping[str, Any]) -> MarkdownTextPostDraft:
    return _load_markdown_text_post_draft_impl(d, public_draft_field_names_map)

def load_public_rich_text_text_post_draft(d: Mapping[str, Any]) -> RichTextTextPostDraft:
    return _load_richtext_text_post_draft_impl(d, public_draft_field_names_map)

def load_public_link_post_draft(d: Mapping[str, Any]) -> LinkPostDraft:
    return _load_link_post_draft_impl(d, public_draft_field_names_map)
