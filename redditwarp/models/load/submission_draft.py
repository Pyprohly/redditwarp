
from __future__ import annotations
from typing import Any, Mapping, Optional

from datetime import datetime, timezone

from ..submission_draft import Draft, MarkdownDraft, RichTextDraft

def load_draft(d: Mapping[str, Any]) -> Draft:
    if d['kind'] == 'markdown':
        return load_markdown_draft(d)
    if d['kind'] == 'richtext':
        return load_rich_text_draft(d)
    raise ValueError('unknown draft type')

def _load_draft_model(d: Mapping[str, Any]) -> Draft:
    created_utms: float = d['created'] / 1000
    modified_utms: float = d['modified'] / 1000

    subreddit_id: Optional[int] = None
    subreddit: Optional[str] = d['subreddit']
    if subreddit is not None:
        _, _, id36 = subreddit.partition('_')
        subreddit_id = int(id36, 36)

    flair: Optional[Draft.FlairInfo] = None
    if df := d['flair']:
        flair = Draft.FlairInfo(
            uuid=df['templateId'],
            type=df['type'],
            text_override=df['text'],
            bg_color=df['backgroundColor'],
            fg_light_or_dark=df['textColor'],
        )

    return Draft(
        d=d,
        uuid=d['id'],
        created_at=datetime.fromtimestamp(created_utms, timezone.utc),
        modified_at=datetime.fromtimestamp(modified_utms, timezone.utc),
        public=d['is_public_link'],
        subreddit_id=subreddit_id,
        title=d['title'],
        reply_notifications=d['send_replies'],
        spoiler=d['spoiler'],
        nsfw=d['nsfw'],
        oc=d['original_content'],
        flair=flair,
    )

def load_markdown_draft(d: Mapping[str, Any]) -> MarkdownDraft:
    t = _load_draft_model(d)
    return MarkdownDraft(
        d=t.d,
        uuid=t.uuid,
        created_at=t.created_at,
        modified_at=t.modified_at,
        public=t.public,
        subreddit_id=t.subreddit_id,
        title=t.title,
        reply_notifications=t.reply_notifications,
        spoiler=t.spoiler,
        nsfw=t.nsfw,
        oc=t.oc,
        flair=t.flair,
        body=d['body'],
    )

def load_rich_text_draft(d: Mapping[str, Any]) -> RichTextDraft:
    t = _load_draft_model(d)
    return RichTextDraft(
        d=t.d,
        uuid=t.uuid,
        created_at=t.created_at,
        modified_at=t.modified_at,
        public=t.public,
        subreddit_id=t.subreddit_id,
        title=t.title,
        reply_notifications=t.reply_notifications,
        spoiler=t.spoiler,
        nsfw=t.nsfw,
        oc=t.oc,
        flair=t.flair,
    )




def load_public_draft(d: Mapping[str, Any]) -> Draft:
    if d['kind'] == 'markdown':
        return load_public_markdown_draft(d)
    if d['kind'] == 'richtext':
        return load_public_rich_text_draft(d)
    raise ValueError('unknown draft type')

def _load_public_draft_model(d: Mapping[str, Any]) -> Draft:
    created_utms: float = d['created'] / 1000
    modified_utms: float = d['modified'] / 1000

    subreddit_id: Optional[int] = None
    subreddit: Optional[str] = d['subredditId']
    if subreddit is not None:
        _, _, id36 = subreddit.partition('_')
        subreddit_id = int(id36, 36)

    flair: Optional[Draft.FlairInfo] = None
    if df := d['flair']:
        flair = Draft.FlairInfo(
            uuid=df['templateId'],
            type=df['type'],
            text_override=df['text'],
            bg_color=df['backgroundColor'],
            fg_light_or_dark=df['textColor'],
        )

    return Draft(
        d=d,
        uuid=d['id'],
        created_at=datetime.fromtimestamp(created_utms, timezone.utc),
        modified_at=datetime.fromtimestamp(modified_utms, timezone.utc),
        public=d['isPublicLink'],
        subreddit_id=subreddit_id,
        title=d['title'],
        reply_notifications=d['sendReplies'],
        spoiler=d['isSpoiler'],
        nsfw=d['isNSFW'],
        oc=d['isOriginalContent'],
        flair=flair,
    )

def load_public_markdown_draft(d: Mapping[str, Any]) -> MarkdownDraft:
    t = _load_public_draft_model(d)
    return MarkdownDraft(
        d=t.d,
        uuid=t.uuid,
        created_at=t.created_at,
        modified_at=t.modified_at,
        public=t.public,
        subreddit_id=t.subreddit_id,
        title=t.title,
        reply_notifications=t.reply_notifications,
        spoiler=t.spoiler,
        nsfw=t.nsfw,
        oc=t.oc,
        flair=t.flair,
        body=d['body'],
    )

def load_public_rich_text_draft(d: Mapping[str, Any]) -> RichTextDraft:
    t = _load_public_draft_model(d)
    return RichTextDraft(
        d=t.d,
        uuid=t.uuid,
        created_at=t.created_at,
        modified_at=t.modified_at,
        public=t.public,
        subreddit_id=t.subreddit_id,
        title=t.title,
        reply_notifications=t.reply_notifications,
        spoiler=t.spoiler,
        nsfw=t.nsfw,
        oc=t.oc,
        flair=t.flair,
    )
