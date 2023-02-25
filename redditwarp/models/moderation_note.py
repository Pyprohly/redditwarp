
from typing import Any, Mapping, Optional

from datetime import datetime
from dataclasses import dataclass

from .datamemento import DatamementoDataclassesMixin

@dataclass(repr=False, eq=False)
class ModerationNote(DatamementoDataclassesMixin):
    #_: KW_ONLY
    d: Mapping[str, Any]
    uuid: str
    unixtime: int
    ("""
        Unix timestamp of when the mod note entry was made.
        """)
    datetime: datetime
    ("""
        Datetime object of when the mod note entry was made.
        """)
    label: str
    subreddit_id: int
    ("""
        ID of the subreddit in which this note belongs.
        """)
    subreddit: str
    ("""
        Name of the subreddit in which this note belongs.
        """)
    agent_id: int
    ("""
        User ID of the moderator associated with this note.
        """)
    agent: str
    ("""
        Name of the moderator associated with this note.
        """)
    target_id: int
    ("""
        ID of the user who this note applies to.
        """)
    target: str
    ("""
        Name of the user who this note applies to.
        """)

@dataclass(repr=False, eq=False)
class ModerationActionNote(ModerationNote):
    label: str
    ("""
        Values: `APPROVAL`, `REMOVAL`, `BAN`, `MUTE`,
        `INVITE`, `SPAM`, `CONTENT_CHANGE`, `MOD_ACTION`.
        """)
    action: str
    ("""
        Name of the mod log action. In lowercase.
        """)

@dataclass(repr=False, eq=False)
class ModerationUserNote(ModerationNote):
    label: str
    ("""
        Values: empty string, `ABUSE_WARNING`, `SPAM_WARNING`, `SPAM_WATCH`,
        `SOLID_CONTRIBUTOR`, `HELPFUL_USER`, `BOT_BAN`, `PERMA_BAN`, `BAN`.

        Value empty string if no label was assigned to this note.
        """)
    note: str
    ("""
        Content of the user note.
        """)
    has_anchor: bool
    ("""
        Whether this note is associated with a submission or comment.

        If true then either :attr:`anchor_submission_id` or :attr:`anchor_comment_id` will be non-`None`.
        """)
    anchor_submission_id: Optional[int]
    ("""
        The submission ID associated with this user note.
        """)
    anchor_comment_id: Optional[int]
    ("""
        The comment ID associated with this user note.
        """)
