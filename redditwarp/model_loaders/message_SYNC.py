
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping, Sequence
if TYPE_CHECKING:
    from ..client_SYNC import Client

from ..models.message_SYNC import MailboxMessage, ComposedMessage, CommentMessage
from .message import (
    load_composed_message as load_base_composed_message,
    load_comment_message as load_base_comment_message,
)

def load_composed_message(d: Mapping[str, Any], client: Client) -> ComposedMessage:
    up = load_base_composed_message(d)
    return ComposedMessage(
        d=up.d,
        subject=up.subject,
        author_name=up.author_name,
        unread=up.unread,
        id=up.id,
        unixtime=up.unixtime,
        datetime=up.datetime,
        body=up.body,
        body_html=up.body_html,
        distinguished=up.distinguished,
        source_user_name=up.source_user_name,
        source_subreddit_name=up.source_subreddit_name,
        destination_user_name=up.destination_user_name,
        destination_subreddit_name=up.destination_subreddit_name,
        source_user_id=up.source_user_id,
        client=client,
    )

def load_comment_message(d: Mapping[str, Any], client: Client) -> CommentMessage:
    up = load_base_comment_message(d)
    return CommentMessage(
        d=up.d,
        subject=up.subject,
        author_name=up.author_name,
        unread=up.unread,
        cause=up.cause,
        submission=up.submission,
        comment=up.comment,
        client=client,
    )

def load_mailbox_message(d: Mapping[str, Any], client: Client) -> MailboxMessage:
    if d['was_comment']:
        return load_comment_message(d, client)
    return load_composed_message(d, client)

def load_composed_message_thread(d: Mapping[str, Any], client: Client) -> Sequence[ComposedMessage]:
    first = load_composed_message(d, client)
    children = []
    if replies := d['replies']:
        children = [load_composed_message(d['data'], client) for d in replies['data']['children']]
    return [first] + children
