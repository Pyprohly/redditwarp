
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .mixins.message import (
    MailboxMessage as MailboxMessageMixin,
    ComposedMessage as ComposedMessageMixin,
    CommentMessage as CommentMessageMixin,
)

class MailboxMessage(MailboxMessageMixin):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client = client

class ComposedMessage(MailboxMessage, ComposedMessageMixin):
    pass

class CommentMessage(MailboxMessage, CommentMessageMixin):
    pass
