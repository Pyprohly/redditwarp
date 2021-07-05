
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_ASYNC import Client

from .message_base import (  # noqa: F401
    MailboxMessage as MailboxMessage,
    ComposedMessage as ComposedMessageBase,
    CommentMessage as CommentMessageBase,
)

class ComposedMessage(ComposedMessageBase):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client = client

class CommentMessage(CommentMessageBase):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client = client