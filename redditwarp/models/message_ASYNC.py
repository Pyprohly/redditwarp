
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_ASYNC import Client

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
    async def reply(self, body: str) -> ComposedMessage:
        return await self.client.p.message.reply(self.id, body)

    async def mark_read(self) -> None:
        await self.client.p.message.mark_read(self.id)

    async def mark_unread(self) -> None:
        await self.client.p.message.mark_unread(self.id)

class CommentMessage(Message, BaseCommentMessage):
    async def mark_read(self) -> None:
        await self.client.p.message.mark_comment_read(self.comment.id)

    async def mark_unread(self) -> None:
        await self.client.p.message.mark_comment_unread(self.comment.id)
