
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .message_base import (  # noqa: F401
    MailboxMessage as MailboxMessage,
    ComposedMessage as ComposedMessage,
    UserMessage as UserMessageBase,
    SubredditMessage as SubredditMessageBase,
    CommentMessage as CommentMessageBase,
)

class UserMessage(UserMessageBase):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client = client

class SubredditMessage(SubredditMessageBase):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client = client

class CommentMessage(CommentMessageBase):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client = client
