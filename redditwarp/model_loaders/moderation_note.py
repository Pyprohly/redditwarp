
from __future__ import annotations
from typing import Any, Mapping

from datetime import datetime, timezone

from ..models.moderation_note import ModerationNote, ModerationActionNote, ModerationUserNote

def load_moderation_note(d: Mapping[str, Any]) -> ModerationNote:
    if d['type'] == 'NOTE':
        return load_moderation_user_note(d)
    return load_moderation_action_note(d)

def load_moderation_action_note(d: Mapping[str, Any]) -> ModerationActionNote:
    return ModerationActionNote(
        d=d,
        uuid=d['id'].partition('_')[-1],
        unixtime=(unixtime := int(d['created_at'])),
        datetime=datetime.fromtimestamp(unixtime, timezone.utc),
        label=d['type'],
        subreddit_id=int(d['subreddit_id'].partition('_')[-1], 36),
        subreddit=d['subreddit'],
        agent_id=int(d['operator_id'].partition('_')[-1], 36),
        agent=d['operator'],
        target_id=int(d['user_id'].partition('_')[-1], 36),
        target=d['user'],
        action=d['mod_action_data']['action'],
    )

def load_moderation_user_note(d: Mapping[str, Any]) -> ModerationUserNote:
    d_user_note_data = d['user_note_data']

    anchor_submission_id = None
    anchor_comment_id = None
    reddit_id: str = d_user_note_data['reddit_id'] or ''
    if reddit_id:
        thing, _, id36 = reddit_id.partition('_')
        idn = int(id36, 36)
        if thing == 't3':
            anchor_submission_id = idn
        elif thing == 't1':
            anchor_comment_id = idn

    return ModerationUserNote(
        d=d,
        uuid=d['id'].partition('_')[-1],
        unixtime=(unixtime := int(d['created_at'])),
        datetime=datetime.fromtimestamp(unixtime, timezone.utc),
        subreddit_id=int(d['subreddit_id'].partition('_')[-1], 36),
        subreddit=d['subreddit'],
        agent_id=int(d['operator_id'].partition('_')[-1], 36),
        agent=d['operator'],
        target_id=int(d['user_id'].partition('_')[-1], 36),
        target=d['user'],
        note=d_user_note_data['note'],
        label=d_user_note_data['label'] or '',
        has_anchor=bool(reddit_id),
        anchor_submission_id=anchor_submission_id,
        anchor_comment_id=anchor_comment_id,
    )
