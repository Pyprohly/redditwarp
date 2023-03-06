
from __future__ import annotations
from typing import Any, Mapping, Optional, Sequence

from datetime import datetime, timezone

from ..core.const import AUTHORIZATION_BASE_URL
from ..models.message import CommentMessageCause, MailboxMessage, ComposedMessage, CommentMessage

def load_mailbox_message(d: Mapping[str, Any]) -> MailboxMessage:
    return MailboxMessage(
        d=d,
        subject=d['subject'],
        author_name=d['author'] or '',
        unread=d['new'],
    )

def load_composed_message(d: Mapping[str, Any]) -> ComposedMessage:
    src_user_name: Optional[str] = d['author']
    src_subr_name: Optional[str] = None
    dst_user_name: Optional[str] = None
    dst_subr_name: Optional[str] = None
    dest: str = d['dest']
    if dest.startswith('#'):
        dst_subr_name = dest.lstrip('#')
    else:
        src_subr_name = d['subreddit']
        dst_user_name = dest

    up = load_mailbox_message(d)
    return ComposedMessage(
        d=up.d,
        subject=up.subject,
        author_name=up.author_name,
        unread=up.unread,
        id=int(d['id'], 36),
        unixtime=(unixtime := int(d['created_utc'])),
        datetime=datetime.fromtimestamp(unixtime, timezone.utc),
        body=d['body'],
        body_html=d['body_html'],
        distinguished=d['distinguished'] or '',
        src_user_name=src_user_name,
        src_subr_name=src_subr_name,
        dst_user_name=dst_user_name,
        dst_subr_name=dst_subr_name,
        src_user_id=(
            int(x.partition('_')[2], 36)
            if (x := d['author_fullname']) else
            {
                None: None,
                'reddit': 81524,
                'welcomebot': 404087392163,
            }.get(src_user_name)
        ),
    )

def load_comment_message(d: Mapping[str, Any]) -> CommentMessage:
    up = load_mailbox_message(d)
    return CommentMessage(
        d=up.d,
        subject=up.subject,
        author_name=up.author_name,
        unread=up.unread,
        cause={
            'username_mention': CommentMessageCause.USERNAME_MENTION,
            'post_reply': CommentMessageCause.SUBMISSION_REPLY,
            'comment_reply': CommentMessageCause.COMMENT_REPLY,
        }[d['type']],
        submission=CommentMessage.Submission(
            id=int((context := d['context']).split('/', 5)[4], 36),
            title=d['link_title'],
            comment_count=d['num_comments'],
            permalink_path=(permalink_path := '/'.join(context.split('/', 6)[:-1]) + '/'),
            permalink=AUTHORIZATION_BASE_URL + permalink_path,
        ),
        comment=CommentMessage.Comment(
            id=int(d['id'], 36),
            created_ut=(created_ut := int(d['created_utc'])),
            created_at=datetime.fromtimestamp(created_ut, timezone.utc),
            author_name=d['author'],
            author_id=int(d['author_fullname'].partition('_')[2], 36),
            subreddit_name=d['subreddit'],
            permalink_path=(permalink_path := context.partition('?')[0]),
            permalink=AUTHORIZATION_BASE_URL + permalink_path,
            is_top_level=(is_top_level := (parent_id := d['parent_id']).startswith('t3_')),
            has_parent_comment=(has_parent_comment := not is_top_level),
            parent_comment_id36=(parent_comment_id36 := parent_id.partition('_')[2] if has_parent_comment else ''),
            parent_comment_id=int(parent_comment_id36, 36) if has_parent_comment else 0,
            score=d['score'],
            body=d['body'],
            body_html=d['body_html'],
            voted={False: -1, None: 0, True: 1}[d['likes']],
        ),
    )


def load_composed_message_thread(d: Mapping[str, Any]) -> Sequence[ComposedMessage]:
    first = load_composed_message(d)
    children = []
    if replies := d['replies']:
        children = [load_composed_message(d['data']) for d in replies['data']['children']]
    return [first] + children
