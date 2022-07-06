
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..client_SYNC import Client

from dataclasses import dataclass

from .message_base import (
    BaseMailboxMessage,
    BaseComposedMessage,
    BaseCommentMessage,
)

@dataclass(repr=False, eq=False)
class MailboxMessage(BaseMailboxMessage):
    client: Client

@dataclass(repr=False, eq=False)
class ComposedMessage(MailboxMessage, BaseComposedMessage):
    def reply(self, body: str) -> ComposedMessage:
        return self.client.p.message.reply(self.id, body)

    def mark_read(self) -> None:
        self.client.p.message.mark_read(self.id)

    def mark_unread(self) -> None:
        self.client.p.message.mark_unread(self.id)

@dataclass(repr=False, eq=False)
class CommentMessage(MailboxMessage, BaseCommentMessage):
    def mark_read(self) -> None:
        self.client.p.message.mark_comment_read(self.comment.id)

    def mark_unread(self) -> None:
        self.client.p.message.mark_comment_unread(self.comment.id)
