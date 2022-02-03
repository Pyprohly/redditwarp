
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
    def reply(self, body: str) -> ComposedMessage:
        return self.client.p.message.reply(self.id, body)

    def mark_read(self) -> None:
        self.client.p.message.mark_read(self.id)

    def mark_unread(self) -> None:
        self.client.p.message.mark_unread(self.id)

class CommentMessage(Message, BaseCommentMessage):
    def mark_read(self) -> None:
        self.client.p.message.mark_comment_read(self.comment.id)

    def mark_unread(self) -> None:
        self.client.p.message.mark_comment_unread(self.comment.id)
