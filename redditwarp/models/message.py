
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from datetime import datetime as DateTime

from dataclasses import dataclass
from enum import Enum, auto

from .artifact import IArtifact

class CommentMessageCause(Enum):
    USERNAME_MENTION = auto()
    SUBMISSION_REPLY = auto()
    COMMENT_REPLY = auto()

@dataclass(repr=False, eq=False)
class MailboxMessage(IArtifact):
    d: Mapping[str, Any]
    subject: str
    ("""
        Subject of the message.

        If a comment message (i.e., :class:`CommentMessage`) then the value will be:

        * `comment reply` if a comment reply.
        * `post reply` if a post reply.
        * `username mention` if a username mention.
        """)
    author_name: str
    unread: bool

@dataclass(repr=False, eq=False)
class ComposedMessage(MailboxMessage):
    id: int
    unixtime: int
    ("""
        Unix timestamp of when the composed message was sent.
        """)
    datetime: DateTime
    ("""
        A datetime object of when the composed message was sent.
        """)
    body: str
    ("""
        The message content.
        """)
    body_html: str
    ("""
        The message content as HTML.
        """)
    unread: bool
    ("""
        Whether the message is new.
        """)
    distinguished: str
    ("""
        Either: `moderator`, `admin`, `gold-auto`, or empty string.

        Empty string if not distinguished.
        """)
    src_user_name: str
    ("""
        Name of the user who sent the message.

        Empty string if the message came from a subreddit.
        """)
    src_subr_name: str
    ("""
        Name of the subreddit in which the message was sent.

        Empty string if the message came from a user.
        """)
    dst_user_name: str
    ("""
        Username of the recipient.

        Empty string if the message was sent to a subreddit.
        """)
    dst_subr_name: str
    ("""
        Name of the subreddit in which the message was sent to.

        Empty string if the message was sent to a user.
        """)
    src_user_id: int
    ("""
        ID of the user who sent the message.

        Value is `-1` if the message came from a subreddit.
        """)

@dataclass(repr=False, eq=False)
class CommentMessage(MailboxMessage):
    @dataclass(repr=False, eq=False)
    class Submission:
        id: int
        title: str
        rel_permalink: str
        permalink: str
        comment_count: int

    @dataclass(repr=False, eq=False)
    class Comment:
        id: int
        created_ut: int
        created_at: DateTime
        author_name: str
        author_id: int
        subreddit_name: str
        rel_permalink: str
        permalink: str
        is_top_level: bool
        has_parent_comment: bool
        parent_comment_id36: str
        parent_comment_id: int
        score: int
        body: str
        body_html: str
        voted: int

    cause: CommentMessageCause
    submission: CommentMessage.Submission
    comment: CommentMessage.Comment
