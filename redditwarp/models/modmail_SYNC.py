
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .modmail_base import (
    BaseConversation,
    BaseMessage,
    BaseModmailModAction,
    BaseUserDossier,
    GenericBaseConversationAggregate,
    GenericBaseUserDossierConversationAggregate,
    GenericBaseOptionalUserDossierConversationAggregate,
)

class Conversation(BaseConversation):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client: Client = client

class Message(BaseMessage):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client: Client = client

class ModmailModAction(BaseModmailModAction):
    pass

class UserDossier(BaseUserDossier):
    pass


class ConversationAggregate(GenericBaseConversationAggregate[Conversation, Message, ModmailModAction]):
    pass

class UserDossierConversationAggregate(GenericBaseUserDossierConversationAggregate[Conversation, Message, ModmailModAction, UserDossier]):
    pass

class OptionalUserDossierConversationAggregate(GenericBaseOptionalUserDossierConversationAggregate[Conversation, Message, ModmailModAction, UserDossier]):
    pass
