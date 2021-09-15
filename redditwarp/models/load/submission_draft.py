
from __future__ import annotations
from typing import Any, Mapping, Optional, Sequence

from datetime import datetime, timezone

from ..submission_draft import Draft, MarkdownDraft, RichTextDraft


draft_column_names_table: Mapping[str, Sequence[str]] = {
    'id': ['id', 'id'],
    'kind': ['kind', 'kind'],
    'created': ['created', 'created'],
    'modified': ['modified', 'modified'],
    'is_public_link': ['is_public_link', 'isPublicLink'],
    'subreddit': ['subreddit', 'subredditId'],
    'title': ['title', 'title'],
    'body': ['body', 'body'],
    'send_replies': ['send_replies', 'sendReplies'],
    'spoiler': ['spoiler', 'isSpoiler'],
    'nsfw': ['nsfw', 'isNSFW'],
    'original_content': ['original_content', 'isOriginalContent'],
    'flair': ['flair', 'flair'],
}
normal_draft_column_names_map: Mapping[str, str] = {k: v[0] for k, v in draft_column_names_table.items()}
public_draft_column_names_map: Mapping[str, str] = {k: v[1] for k, v in draft_column_names_table.items()}


def _load_some_draft(d: Mapping[str, Any], h: Mapping[str, str]) -> Draft:
    if d[h['kind']] == 'markdown':
        return load_markdown_draft(d)
    if d[h['kind']] == 'richtext':
        return load_rich_text_draft(d)
    raise ValueError('unknown draft type')

def _construct_some_draft(d: Mapping[str, Any], h: Mapping[str, str]) -> Draft:
    created_utms: float = d[h['created']] / 1000
    modified_utms: float = d[h['modified']] / 1000

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
        created_at=datetime.fromtimestamp(created_utms, timezone.utc),
        modified_at=datetime.fromtimestamp(modified_utms, timezone.utc),
        public=d[h['is_public_link']],
        subreddit_id=subreddit_id,
        title=d[h['title']],
        reply_notifications=d[h['send_replies']],
        spoiler=d[h['spoiler']],
        nsfw=d[h['nsfw']],
        oc=d[h['original_content']],
        flair=flair,
    )

def _load_some_markdown_draft(d: Mapping[str, Any], h: Mapping[str, str]) -> MarkdownDraft:
    u = construct_draft(d)
    return MarkdownDraft(
        d=u.d,
        uuid=u.uuid,
        created_at=u.created_at,
        modified_at=u.modified_at,
        public=u.public,
        subreddit_id=u.subreddit_id,
        title=u.title,
        reply_notifications=u.reply_notifications,
        spoiler=u.spoiler,
        nsfw=u.nsfw,
        oc=u.oc,
        flair=u.flair,
        #,
        body=d['body'],
    )

def _load_some_rich_text_draft(d: Mapping[str, Any], h: Mapping[str, str]) -> RichTextDraft:
    u = construct_draft(d)
    return RichTextDraft(
        d=u.d,
        uuid=u.uuid,
        created_at=u.created_at,
        modified_at=u.modified_at,
        public=u.public,
        subreddit_id=u.subreddit_id,
        title=u.title,
        reply_notifications=u.reply_notifications,
        spoiler=u.spoiler,
        nsfw=u.nsfw,
        oc=u.oc,
        flair=u.flair,
    )


def load_draft(d: Mapping[str, Any]) -> Draft:
    return _load_some_draft(d, normal_draft_column_names_map)

def construct_draft(d: Mapping[str, Any]) -> Draft:
    return _construct_some_draft(d, normal_draft_column_names_map)

def load_markdown_draft(d: Mapping[str, Any]) -> MarkdownDraft:
    return _load_some_markdown_draft(d, normal_draft_column_names_map)

def load_rich_text_draft(d: Mapping[str, Any]) -> RichTextDraft:
    return _load_some_rich_text_draft(d, normal_draft_column_names_map)


def load_public_draft(d: Mapping[str, Any]) -> Draft:
    return _load_some_draft(d, public_draft_column_names_map)

def construct_public_draft(d: Mapping[str, Any]) -> Draft:
    return _construct_some_draft(d, public_draft_column_names_map)

def load_public_markdown_draft(d: Mapping[str, Any]) -> MarkdownDraft:
    return _load_some_markdown_draft(d, public_draft_column_names_map)

def load_public_rich_text_draft(d: Mapping[str, Any]) -> RichTextDraft:
    return _load_some_rich_text_draft(d, public_draft_column_names_map)
