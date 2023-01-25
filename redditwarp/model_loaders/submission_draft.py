
from __future__ import annotations
from typing import Any, Mapping, Optional

from datetime import datetime, timezone

from ..models.submission_draft import Draft, MarkdownDraft, RichTextDraft


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


def _load_draft_impl(d: Mapping[str, Any], h: Mapping[str, str]) -> Draft:
    if d[h['kind']] == 'markdown':
        return load_markdown_draft(d)
    if d[h['kind']] == 'richtext':
        return load_rich_text_draft(d)
    raise ValueError('unknown draft type')

def _xload_draft_impl(d: Mapping[str, Any], h: Mapping[str, str]) -> Draft:
    created_ts: float = d[h['created']] / 1000
    modified_ts: float = d[h['modified']] / 1000

    subreddit_id: Optional[int] = None
    subreddit: Optional[str] = d[h['subreddit']]
    if subreddit is not None:
        _, _, id36 = subreddit.partition('_')
        subreddit_id = int(id36, 36)

    flair: Optional[Draft.FlairInfo] = None
    if df := d[h['flair']]:
        flair = Draft.FlairInfo(
            uuid=df['templateId'],
            type=df['type'],
            text_override=df['text'],
            bg_color=df['backgroundColor'],
            fg_light_or_dark=df['textColor'],
        )

    return Draft(
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
        original_content=d[h['original_content']],
        flair=flair,
    )

def _load_markdown_draft_impl(d: Mapping[str, Any], h: Mapping[str, str]) -> MarkdownDraft:
    up = xload_draft(d)
    return MarkdownDraft(
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
        original_content=up.original_content,
        flair=up.flair,
        body=d['body'],
    )

def _load_rich_text_draft_impl(d: Mapping[str, Any], h: Mapping[str, str]) -> RichTextDraft:
    up = xload_draft(d)
    return RichTextDraft(
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
        original_content=up.original_content,
        flair=up.flair,
    )


def load_draft(d: Mapping[str, Any]) -> Draft:
    return _load_draft_impl(d, normal_draft_field_names_map)

def xload_draft(d: Mapping[str, Any]) -> Draft:
    return _xload_draft_impl(d, normal_draft_field_names_map)

def load_markdown_draft(d: Mapping[str, Any]) -> MarkdownDraft:
    return _load_markdown_draft_impl(d, normal_draft_field_names_map)

def load_rich_text_draft(d: Mapping[str, Any]) -> RichTextDraft:
    return _load_rich_text_draft_impl(d, normal_draft_field_names_map)


def load_public_draft(d: Mapping[str, Any]) -> Draft:
    return _load_draft_impl(d, public_draft_field_names_map)

def xload_public_draft(d: Mapping[str, Any]) -> Draft:
    return _xload_draft_impl(d, public_draft_field_names_map)

def load_public_markdown_draft(d: Mapping[str, Any]) -> MarkdownDraft:
    return _load_markdown_draft_impl(d, public_draft_field_names_map)

def load_public_rich_text_draft(d: Mapping[str, Any]) -> RichTextDraft:
    return _load_rich_text_draft_impl(d, public_draft_field_names_map)
