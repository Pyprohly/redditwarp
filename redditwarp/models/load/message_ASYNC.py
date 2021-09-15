
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping, Sequence
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ..message_ASYNC import Message

from itertools import chain

from ..message_ASYNC import ComposedMessage, CommentMessage

def load_composed_message(d: Mapping[str, Any], client: Client) -> ComposedMessage:
    return ComposedMessage(d, client)

def load_comment_message(d: Mapping[str, Any], client: Client) -> CommentMessage:
    return CommentMessage(d, client)

def load_message(d: Mapping[str, Any], client: Client) -> Message:
    if d['was_comment']:
        return load_comment_message(d, client)
    return load_composed_message(d, client)

def load_threaded_message(d: Mapping[str, Any], client: Client) -> Sequence[ComposedMessage]:
    first = load_composed_message(d, client)
    children = []
    if replies := d['replies']:
        children = [load_composed_message(d['data'], client) for d in replies['data']['children']]
    return list(chain([first], children))
