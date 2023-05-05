
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any, Optional
if TYPE_CHECKING:
    from datetime import datetime as DateTime

from dataclasses import dataclass
from enum import Enum, auto

from .datamemento import DatamementoDataclassesMixin

class CommentMessageCause(Enum):
    USERNAME_MENTION = auto()
    SUBMISSION_REPLY = auto()
    COMMENT_REPLY = auto()

@dataclass(repr=False, eq=False)
class MailboxMessage(DatamementoDataclassesMixin):
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
    ("""
        Author name.

        Unknown what happens if the user is deleted.
        Is the value `[deleted]`, an empty string, or does the field in the
        underlying object not exist?
        If you have any information about this, please open an issue report at
        `<https://github.com/Pyprohly/redditwarp/issues>`_.
        """)
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
    src_user_name: Optional[str]
    ("""
        Username of the sender.
        """)
    src_subr_name: Optional[str]
    ("""
        Name of the subreddit in which the message was sent from.
        """)
    dst_user_name: Optional[str]
    ("""
        Username of the recipient.
        """)
    dst_subr_name: Optional[str]
    ("""
        Name of the subreddit in which the message was sent to.
        """)
    src_user_id: Optional[int]
    ("""
        ID of the user who sent the message.
        """)

@dataclass(repr=False, eq=False)
class CommentMessage(MailboxMessage):
    @dataclass(repr=False, eq=False)
    class Submission:
        id: int
        title: str
        permalink_path: str
        permalink: str
        comment_count: int

    @dataclass(repr=False, eq=False)
    class Comment:
        id: int
        created_ut: int
        created_at: DateTime
        author_name: str
        ("""
            Author name.

            Unknown what happens if the user is deleted.
            Is the value `[deleted]`, an empty string, or does the field in the
            underlying object not exist?
            If you have any information about this, please open an issue report at
            `<https://github.com/Pyprohly/redditwarp/issues>`_.
            """)
        author_id: int
        ("""
            Author ID.

            Unknown what happens if the user is deleted.
            If you have any information about this, please open an issue report at
            `<https://github.com/Pyprohly/redditwarp/issues>`_.
            """)
        subreddit_name: str
        ("""
            Subreddit name.

            Unknown what happens if the subreddit is deleted.
            Is the value `[deleted]`, an empty string, or does the field in the
            underlying object not exist?
            If you have any information about this, please open an issue report at
            `<https://github.com/Pyprohly/redditwarp/issues>`_.
            """)
        permalink_path: str
        permalink: str
        is_top_level: bool
        has_parent_comment: bool
        parent_comment_id36: str
        parent_comment_idn: int
        parent_comment_id: int
        score: int
        body: str
        body_html: str
        voted: int

    cause: CommentMessageCause
    submission: CommentMessage.Submission
    comment: CommentMessage.Comment
