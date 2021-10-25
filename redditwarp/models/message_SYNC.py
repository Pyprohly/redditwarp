
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .message_base import (
    BaseMessage,
    BaseComposedMessage,
    BaseCommentMessage,
)

class Message(BaseMessage):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client: Client = client

class ComposedMessage(Message, BaseComposedMessage):
    pass

class CommentMessage(Message, BaseCommentMessage):
    pass
