
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from datetime import datetime as DateTime
    from .message import CommentMessageCause

from dataclasses import dataclass

from .artifact import IArtifact

@dataclass(repr=False, eq=False)
class BaseMailboxMessage(IArtifact):
    d: Mapping[str, Any]
    subject: str
    author_name: str
    unread: bool

@dataclass(repr=False, eq=False)
class BaseComposedMessage(BaseMailboxMessage):
    id: int
    unixtime: int
    datetime: DateTime
    body: str
    body_html: str
    unread: bool
    distinguished: str
    source_user_name: str
    source_subreddit_name: str
    destination_user_name: str
    destination_subreddit_name: str
    source_user_id: int

@dataclass(repr=False, eq=False)
class BaseCommentMessage(BaseMailboxMessage):
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
    submission: BaseCommentMessage.Submission
    comment: BaseCommentMessage.Comment
