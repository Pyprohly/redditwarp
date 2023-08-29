
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any, Sequence, Optional
if TYPE_CHECKING:
    from ..client_ASYNC import Client

from dataclasses import dataclass

from .modmail import (
    ConversationInfo as BaseConversationInfo,
    Message as BaseMessage,
    ModAction as BaseModAction,
    UserDossier as BaseUserDossier,
    ConversationAggregate as BaseConversationAggregate,
)

class ConversationInfo(BaseConversationInfo):
    def __init__(self, d: Mapping[str, Any], client: Client) -> None:
        super().__init__(d)
        self.client: Client = client
        ("")

    async def reply(self, body: str, *, hidden: bool = False, internal: bool = False) -> ConversationAggregate:
        return await self.client.p.modmail.conversation.reply(self.id, body, hidden=hidden, internal=internal)

    async def mark_read(self) -> None:
        await self.client.p.modmail.conversation.mark_read(self.id)

    async def mark_unread(self) -> None:
        await self.client.p.modmail.conversation.mark_unread(self.id)


class Message(BaseMessage):
    def __init__(self, d: Mapping[str, Any], client: Client) -> None:
        super().__init__(d)
        self.client: Client = client
        ("")

class ModAction(BaseModAction):
    pass

class UserDossier(BaseUserDossier):
    pass


@dataclass(repr=False, eq=False, frozen=True)
class ConversationAggregate(BaseConversationAggregate):
    info: ConversationInfo
    history: Sequence[object]
    messages: Sequence[Message]
    actions: Sequence[ModAction]
    user_dossier: Optional[UserDossier]
