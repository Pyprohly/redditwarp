
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .message_base import (
    MailboxMessageMixinBase,
    ComposedMessageMixinBase,
    CommentMessageMixinBase,
)

class MailboxMessage(MailboxMessageMixinBase):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client = client

class ComposedMessage(MailboxMessage, ComposedMessageMixinBase):
    pass

class CommentMessage(MailboxMessage, CommentMessageMixinBase):
    pass
