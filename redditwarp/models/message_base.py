
from __future__ import annotations
from typing import Mapping, Any, Optional

from datetime import datetime, timezone

from ..auth.const import AUTHORIZATION_BASE_URL
from .funbox import FunBox

class MailboxMessage(FunBox):
    pass

class ComposedMessage(MailboxMessage):
    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.id = int(d['id'], 36)
        self.created_ut = int(d['created_utc'])
        self.created_at = datetime.fromtimestamp(self.created_ut, timezone.utc)
        self.recipient: str = d['dest']
        self.subject: str = d['subject']
        self.body: str = d['body']
        self.body_html: str = d['body_html']
        self.unread: bool = d['new']
        self.distinguished: str = d['distinguished'] or ''
        # self.replies: Optional[]: int

        _parent_id: Optional[str] = d['parent_id']
        self.is_top_level: bool = _parent_id is None
        self.parent_id: Optional[int] = None
        if _parent_id is not None:
            self.parent_id = int(_parent_id.partition('_')[2], 36)


class UserMessage(ComposedMessage):
    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.sender: str = d['author']
        self.sender_id: Optional[int] = (
            int(v.partition('_')[2], 36)
            if (v := d['author_fullname']) else
            None
        )

class SubredditMessage(ComposedMessage):
    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.subreddit_name: str = d['subreddit']

class CommentMessage(MailboxMessage):
    class SubmissionInfo:
        def __init__(self, d: Mapping[str, Any]):
            self.title: str = d['link_title']
            _context: str = d['context']
            self.id: int = int(_context.split('/', 5)[4], 36)
            self.comment_count: int = d['num_comments']

    class CommentInfo:
        def __init__(self, d: Mapping[str, Any]):
            self.id = int(d['id'], 36)
            self.created_ut = int(d['created_utc'])
            self.created_at = datetime.fromtimestamp(self.created_ut, timezone.utc)
            self.context = d['context']
            self.rel_permalink: str = self.context.partition('?')[0]
            self.permalink: str = AUTHORIZATION_BASE_URL + self.rel_permalink

            _parent_id: str = d['parent_id']
            self.is_top_level: bool = _parent_id.startswith('t3_')
            self.parent_comment_id36: Optional[str] = None
            self.parent_comment_id: Optional[int] = None
            if _parent_id.startswith('t1_'):
                self.parent_comment_id36 = _parent_id.partition('_')[2]
                self.parent_comment_id = int(self.parent_comment_id36, 36)

            self.score: int = d['score']
            self.subreddit_name: str = d['subreddit']
            self.body: str = d['body']
            self.body_html: str = d['body_html']
            self.author_name: str = d['author']
            self.author_id = int(d['author_fullname'].partition('_')[2], 36)

            self.voted: int = {False: -1, None: 0, True: 1}[d['likes']]

    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.type: str = d['type']
        self.submission = self.SubmissionInfo(d)
        self.comment = self.CommentInfo(d)
