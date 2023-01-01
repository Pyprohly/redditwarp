
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any, Sequence, Optional
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .modmail import (
    ConversationInfo as BaseConversationInfo,
    Message as BaseMessage,
    ModAction as BaseModAction,
    UserDossier as BaseUserDossier,
    ConversationAggregate as BaseConversationAggregate,
    UserDossierConversationAggregate as BaseUserDossierConversationAggregate,
    OptionalUserDossierConversationAggregate as BaseOptionalUserDossierConversationAggregate,
)

class ConversationInfo(BaseConversationInfo):
    def __init__(self, d: Mapping[str, Any], client: Client) -> None:
        super().__init__(d)
        self.client: Client = client

    def reply(self, body: str, *, hidden: bool = False, internal: bool = False) -> ConversationAggregate:
        return self.client.p.modmail.conversation.reply(self.id, body, hidden=hidden, internal=internal)

    def mark_read(self) -> None:
        self.client.p.modmail.conversation.mark_read(self.id)

    def mark_unread(self) -> None:
        self.client.p.modmail.conversation.mark_unread(self.id)


class Message(BaseMessage):
    def __init__(self, d: Mapping[str, Any], client: Client) -> None:
        super().__init__(d)
        self.client: Client = client

class ModAction(BaseModAction):
    pass

class UserDossier(BaseUserDossier):
    pass


class ConversationAggregate(BaseConversationAggregate):
    conversation: ConversationInfo
    messages: Sequence[Message]
    mod_actions: Sequence[ModAction]
    history: Sequence[object]

class UserDossierConversationAggregate(BaseUserDossierConversationAggregate):
    conversation: ConversationInfo
    messages: Sequence[Message]
    mod_actions: Sequence[ModAction]
    history: Sequence[object]
    user_dossier: UserDossier

class OptionalUserDossierConversationAggregate(BaseOptionalUserDossierConversationAggregate):
    conversation: ConversationInfo
    messages: Sequence[Message]
    mod_actions: Sequence[ModAction]
    history: Sequence[object]
    user_dossier: Optional[UserDossier]
