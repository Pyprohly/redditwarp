
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..client_ASYNC import Client

from dataclasses import dataclass

from .message import (
    MailboxMessage as BaseMailboxMessage,
    ComposedMessage as BaseComposedMessage,
    CommentMessage as BaseCommentMessage,
)

@dataclass(repr=False, eq=False)
class MailboxMessage(BaseMailboxMessage):
    client: Client

@dataclass(repr=False, eq=False)
class ComposedMessage(MailboxMessage, BaseComposedMessage):
    async def reply(self, body: str) -> ComposedMessage:
        return await self.client.p.message.reply(self.id, body)

    async def mark_read(self) -> None:
        await self.client.p.message.mark_read(self.id)

    async def mark_unread(self) -> None:
        await self.client.p.message.mark_unread(self.id)

@dataclass(repr=False, eq=False)
class CommentMessage(MailboxMessage, BaseCommentMessage):
    async def mark_read(self) -> None:
        await self.client.p.message.mark_comment_read(self.comment.id)

    async def mark_unread(self) -> None:
        await self.client.p.message.mark_comment_unread(self.comment.id)
