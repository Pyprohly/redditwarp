
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ..message_SYNC import MailboxMessage

from ...util.tree_node import GeneralTreeNode
from ..message_SYNC import ComposedMessage, CommentMessage

def load_composed_message(d: Mapping[str, Any], client: Client) -> ComposedMessage:
    return ComposedMessage(d, client)

def load_comment_message(d: Mapping[str, Any], client: Client) -> CommentMessage:
    return CommentMessage(d, client)

def load_mailbox_message(d: Mapping[str, Any], client: Client) -> MailboxMessage:
    if d['was_comment']:
        return load_comment_message(d, client)
    return load_composed_message(d, client)

def load_threaded_message(d: Mapping[str, Any], client: Client) -> GeneralTreeNode[MailboxMessage, MailboxMessage]:
    replies = d['replies']
    children = []
    if replies:
        children = [load_mailbox_message(d['data'], client) for d in replies['data']['children']]
    return GeneralTreeNode(load_mailbox_message(d, client), children)
