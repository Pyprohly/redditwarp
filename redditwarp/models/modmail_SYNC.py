
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .modmail import (
    Conversation as BaseConversation,
    Message as BaseMessage,
    ModmailModAction as BaseModmailModAction,
    UserDossier as BaseUserDossier,
    GBaseConversationAggregate,
    GBaseUserDossierConversationAggregate,
    GBaseOptionalUserDossierConversationAggregate,
)

class Conversation(BaseConversation):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client: Client = client

    def reply(self, body: str, *, hidden: bool = False, internal: bool = False) -> ConversationAggregate:
        return self.client.p.modmail.conversation.reply(self.id, body, hidden=hidden, internal=internal)

    def mark_read(self) -> None:
        self.client.p.modmail.conversation.mark_read(self.id)

    def mark_unread(self) -> None:
        self.client.p.modmail.conversation.mark_unread(self.id)


class Message(BaseMessage):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client: Client = client

class ModmailModAction(BaseModmailModAction):
    pass

class UserDossier(BaseUserDossier):
    pass


class ConversationAggregate(GBaseConversationAggregate[Conversation, Message, ModmailModAction]):
    pass

class UserDossierConversationAggregate(GBaseUserDossierConversationAggregate[Conversation, Message, ModmailModAction, UserDossier]):
    pass

class OptionalUserDossierConversationAggregate(GBaseOptionalUserDossierConversationAggregate[Conversation, Message, ModmailModAction, UserDossier]):
    pass
