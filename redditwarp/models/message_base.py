
from __future__ import annotations
from typing import Mapping, Any, Optional

from datetime import datetime, timezone

from ..auth.const import AUTHORIZATION_BASE_URL
from .artifact import Artifact

class BaseMailboxMessage(Artifact):
    pass

class BaseComposedMessage(BaseMailboxMessage):
    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.id = int(d['id'], 36)
        self.created_ut = int(d['created_utc'])
        self.created_at = datetime.fromtimestamp(self.created_ut, timezone.utc)
        dest: str = d['dest']
        self.dest: str = dest
        self.recipient_name_prefixed: str = 'r/'+dest if dest.startswith('#') else 'u/'+dest
        self.subject: str = d['subject']
        self.body: str = d['body']
        self.body_html: str = d['body_html']
        self.unread: bool = d['new']
        self.distinguished: str = d['distinguished'] or ''
        self.sender: str = d['author'] or ''
        self.sender_id: Optional[int] = (
            int(v.partition('_')[2], 36)
            if (v := d['author_fullname']) else
            None
        )
        self.via: str = '' if dest.startswith('#') else (d['subreddit'] or '')

class BaseCommentMessage(BaseMailboxMessage):
    class SubmissionInfo:
        def __init__(self, d: Mapping[str, Any]):
            self.title: str = d['link_title']
            context: str = d['context']
            self.id: int = int(context.split('/', 5)[4], 36)
            self.comment_count: int = d['num_comments']

    class CommentInfo:
        def __init__(self, d: Mapping[str, Any]):
            self.id = int(d['id'], 36)
            self.created_ut = int(d['created_utc'])
            self.created_at = datetime.fromtimestamp(self.created_ut, timezone.utc)
            self.context = d['context']
            self.rel_permalink: str = self.context.partition('?')[0]
            self.permalink: str = AUTHORIZATION_BASE_URL + self.rel_permalink

            parent_id: str = d['parent_id']
            self.is_top_level: bool = parent_id.startswith('t3_')
            self.parent_comment_id36: Optional[str] = None
            self.parent_comment_id: Optional[int] = None
            if parent_id.startswith('t1_'):
                self.parent_comment_id36 = parent_id.partition('_')[2]
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
