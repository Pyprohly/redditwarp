
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ..message_ASYNC import MailboxMessage, ComposedMessage

from ..message_ASYNC import UserMessage, SubredditMessage, CommentMessage

def load_user_message(d: Mapping[str, Any], client: Client) -> UserMessage:
    return UserMessage(d, client)

def load_subreddit_message(d: Mapping[str, Any], client: Client) -> SubredditMessage:
    return SubredditMessage(d, client)

def load_comment_message(d: Mapping[str, Any], client: Client) -> CommentMessage:
    return CommentMessage(d, client)

def load_mailbox_message(d: Mapping[str, Any], client: Client) -> MailboxMessage:
    if d['was_comment']:
        return load_comment_message(d, client)
    elif d['subreddit'] is None:
        return load_user_message(d, client)
    return load_subreddit_message(d, client)

def load_composed_message(d: Mapping[str, Any], client: Client) -> ComposedMessage:
    if d['subreddit'] is None:
        return load_user_message(d, client)
    return load_subreddit_message(d, client)
