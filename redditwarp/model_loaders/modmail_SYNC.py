
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any, Optional, MutableSequence
if TYPE_CHECKING:
    from ..client_SYNC import Client

from ..models.modmail_SYNC import (
    ConversationInfo,
    Message,
    ModAction,
    UserDossier,
    ConversationAggregate,
)

def load_conversation_info(d: Mapping[str, Any], client: Client) -> ConversationInfo:
    return ConversationInfo(d, client)

def load_message(d: Mapping[str, Any], client: Client) -> Message:
    return Message(d, client)

def load_mod_action(d: Mapping[str, Any]) -> ModAction:
    return ModAction(d)

def load_user_dossier(d: Mapping[str, Any]) -> UserDossier:
    return UserDossier(d)


def load_conversation_aggregate(
    data: Mapping[str, Any],
    *,
    client: Client,
) -> ConversationAggregate:
    conversation_data: Mapping[str, Any] = data['conversation']
    messages_mapping_data: Mapping[str, Any] = data['messages']
    actions_mapping_data: Mapping[str, Any] = data['modActions']
    optional_user_dossier_data: Optional[Mapping[str, Any]] = data['user'] or None

    conversation = load_conversation_info(conversation_data, client)
    user_dossier = None
    if optional_user_dossier_data:
        user_dossier = load_user_dossier(optional_user_dossier_data)

    messages: MutableSequence[Message] = []
    actions: MutableSequence[ModAction] = []
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
            mod_action_data = actions_mapping_data[id36]
            convo_obj = load_mod_action(mod_action_data)
            actions.append(convo_obj)

        if convo_obj is None:
            raise Exception('unknown modmail object type encountered')
        history.append(convo_obj)

    return ConversationAggregate(
        info=conversation,
        history=history,
        messages=messages,
        actions=actions,
        user_dossier=user_dossier,
    )
