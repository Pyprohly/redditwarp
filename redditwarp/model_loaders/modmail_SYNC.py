
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any, Optional, MutableSequence
if TYPE_CHECKING:
    from ..client_SYNC import Client

from ..models.modmail_SYNC import (
    Conversation,
    Message,
    ModmailModAction,
    UserDossier,
    ConversationAggregate,
    UserDossierConversationAggregate,
    OptionalUserDossierConversationAggregate,
)

def load_conversation(d: Mapping[str, Any], client: Client) -> Conversation:
    return Conversation(d, client)

def load_message(d: Mapping[str, Any], client: Client) -> Message:
    return Message(d, client)

def load_modmail_mod_action(d: Mapping[str, Any]) -> ModmailModAction:
    return ModmailModAction(d)

def load_user_dossier(d: Mapping[str, Any]) -> UserDossier:
    return UserDossier(d)


def load_conversation_aggregate(
    conversation_data: Mapping[str, Any],
    messages_mapping_data: Mapping[str, Any],
    mod_actions_mapping_data: Mapping[str, Any],
    *,
    client: Client,
) -> ConversationAggregate:
    conversation = load_conversation(conversation_data, client)

    messages: MutableSequence[Message] = []
    mod_actions: MutableSequence[ModmailModAction] = []
    history: MutableSequence[object] = []

    convo_references = conversation_data['objIds']
    for convo_ref in convo_references:
        key = convo_ref['key']
        id36 = convo_ref['id']

        convo_obj: object = None
        if key == 'messages':
            message_data = messages_mapping_data[id36]
            convo_obj = load_message(message_data, client)
            messages.append(convo_obj)
        elif key == 'modActions':
            mod_action_data = mod_actions_mapping_data[id36]
            convo_obj = load_modmail_mod_action(mod_action_data)
            mod_actions.append(convo_obj)

        if convo_obj is None:
            raise Exception('unknown modmail object type encountered')
        history.append(convo_obj)

    return ConversationAggregate(conversation, messages, mod_actions, history)

def load_user_dossier_conversation_aggregate(
    conversation_data: Mapping[str, Any],
    messages_mapping_data: Mapping[str, Any],
    mod_actions_mapping_data: Mapping[str, Any],
    user_dossier_data: Mapping[str, Any],
    *,
    client: Client,
) -> UserDossierConversationAggregate:
    conversation = load_conversation(conversation_data, client)
    user_dossier = load_user_dossier(user_dossier_data)

    messages: MutableSequence[Message] = []
    mod_actions: MutableSequence[ModmailModAction] = []
    history: MutableSequence[object] = []

    convo_references = conversation_data['objIds']
    for convo_ref in convo_references:
        key = convo_ref['key']
        id36 = convo_ref['id']

        convo_obj: object = None
        if key == 'messages':
            message_data = messages_mapping_data[id36]
            convo_obj = load_message(message_data, client)
            messages.append(convo_obj)
        elif key == 'modActions':
            mod_action_data = mod_actions_mapping_data[id36]
            convo_obj = load_modmail_mod_action(mod_action_data)
            mod_actions.append(convo_obj)

        if convo_obj is None:
            raise Exception('unknown modmail object type encountered')
        history.append(convo_obj)

    return UserDossierConversationAggregate(conversation, messages, mod_actions, history, user_dossier)

def load_optional_user_dossier_conversation_aggregate(
    conversation_data: Mapping[str, Any],
    messages_mapping_data: Mapping[str, Any],
    mod_actions_mapping_data: Mapping[str, Any],
    optional_user_dossier_data: Optional[Mapping[str, Any]],
    *,
    client: Client,
) -> OptionalUserDossierConversationAggregate:
    conversation = load_conversation(conversation_data, client)
    user_dossier = None
    if optional_user_dossier_data is not None:
        user_dossier = load_user_dossier(optional_user_dossier_data)

    messages: MutableSequence[Message] = []
    mod_actions: MutableSequence[ModmailModAction] = []
    history: MutableSequence[object] = []

    convo_references = conversation_data['objIds']
    for convo_ref in convo_references:
        key = convo_ref['key']
        id36 = convo_ref['id']

        convo_obj: object = None
        if key == 'messages':
            message_data = messages_mapping_data[id36]
            convo_obj = load_message(message_data, client)
            messages.append(convo_obj)
        elif key == 'modActions':
            mod_action_data = mod_actions_mapping_data[id36]
            convo_obj = load_modmail_mod_action(mod_action_data)
            mod_actions.append(convo_obj)

        if convo_obj is None:
            raise Exception('unknown modmail object type encountered')
        history.append(convo_obj)

    return OptionalUserDossierConversationAggregate(conversation, messages, mod_actions, history, user_dossier)
