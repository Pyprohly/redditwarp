
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Iterable
if TYPE_CHECKING:
    from ...client_ASYNC import Client

from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_calling_async_iterator import CallChunkCallingAsyncIterator
from ...iterators.call_chunk_chaining_async_iterator import CallChunkChainingAsyncIterator
from ...iterators.async_call_chunk import AsyncCallChunk
from ...models.modmail_ASYNC import (
    Conversation,
    Message,
    ConversationAggregate,
    UserDossierConversationAggregate,
    OptionalUserDossierConversationAggregate,
)
from ...model_loaders.modmail_ASYNC import (
    load_conversation,
    load_message,
    load_conversation_aggregate,
    load_user_dossier_conversation_aggregate,
    load_optional_user_dossier_conversation_aggregate,
)

class ConversationProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client

    async def fetch(self, idn: int, *, mark_read: bool = False) -> OptionalUserDossierConversationAggregate:
        convo_id36 = to_base36(idn)
        root = await self._client.request('GET', f'/api/mod/conversations/{convo_id36}')
        return load_optional_user_dossier_conversation_aggregate(
            root['conversation'],
            root['messages'],
            root['modActions'],
            root['user'] or None,
            client=self._client,
        )

    async def create(self, sr: str, to: str, subject: str, body: str, *, hidden: bool = False) -> tuple[Conversation, Message]:
        data = {'srName': sr, 'to': to, 'subject': subject, 'body': body, 'isAuthorHidden': '01'[hidden]}
        root = await self._client.request('POST', '/api/mod/conversations', data=data)
        conversation_data = root['conversation']
        conversation = load_conversation(conversation_data, self._client)
        message_id36 = conversation_data['objIds'][0]['id']
        message = load_message(root['messages'][message_id36], self._client)
        return (conversation, message)

    async def reply(self, idn: int, body: str, *, hidden: bool = False, internal: bool = False) -> ConversationAggregate:
        data = {'body': body, 'isAuthorHidden': '01'[hidden], 'isInternal': '01'[internal]}
        convo_id36 = to_base36(idn)
        root = await self._client.request('POST', f'/api/mod/conversations/{convo_id36}', data=data)
        conversation_data = root['conversation']
        messages_mapping_data = root['messages']
        mod_actions_mapping_data = conversation_data['modActions']
        return load_conversation_aggregate(
            conversation_data,
            messages_mapping_data,
            mod_actions_mapping_data,
            client=self._client,
        )

    async def mark_read(self, idn: int) -> None:
        data = {'conversationIds': to_base36(idn)}
        await self._client.request('POST', '/api/mod/conversations/read', data=data)

    def bulk_mark_read(self, ids: Iterable[int]) -> CallChunkCallingAsyncIterator[None]:
        async def mass_mark_read(ids: Sequence[int]) -> None:
            id36s = map(to_base36, ids)
            ids_str = ','.join(id36s)
            await self._client.request('POST', '/api/mod/conversations/read', data={'conversationIds': ids_str})

        return CallChunkCallingAsyncIterator(AsyncCallChunk(mass_mark_read, chunk) for chunk in chunked(ids, 100))

    async def mark_unread(self, idn: int) -> None:
        data = {'conversationIds': to_base36(idn)}
        await self._client.request('POST', '/api/mod/conversations/unread', data=data)

    def bulk_mark_unread(self, ids: Iterable[int]) -> CallChunkCallingAsyncIterator[None]:
        async def mass_mark_unread(ids: Sequence[int]) -> None:
            id36s = map(to_base36, ids)
            ids_str = ','.join(id36s)
            await self._client.request('POST', '/api/mod/conversations/unread', data={'conversationIds': ids_str})

        return CallChunkCallingAsyncIterator(AsyncCallChunk(mass_mark_unread, chunk) for chunk in chunked(ids, 100))

    def bulk_mark_all_read(self, mailbox: str, subrs: Iterable[str]) -> CallChunkChainingAsyncIterator[int]:
        async def mass_mark_all_read(subrs: Sequence[str]) -> Sequence[int]:
            subrs_str = ','.join(subrs)
            data = {'state': mailbox, 'entity': subrs_str}
            root = await self._client.request('POST', '/api/mod/conversations/bulk/read', data=data)
            return [int(id36, 36) for id36 in root['conversation_ids']]

        return CallChunkChainingAsyncIterator(AsyncCallChunk(mass_mark_all_read, chunk) for chunk in chunked(subrs, 100))

    async def highlight(self, idn: int) -> ConversationAggregate:
        convo_id36 = to_base36(idn)
        root = await self._client.request('POST', f'/api/mod/conversations/{convo_id36}/highlight')
        return load_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            client=self._client,
        )

    async def unhighlight(self, idn: int) -> ConversationAggregate:
        convo_id36 = to_base36(idn)
        root = await self._client.request('DELETE', f'/api/mod/conversations/{convo_id36}/highlight')
        return load_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            client=self._client,
        )

    async def archive(self, idn: int) -> ConversationAggregate:
        convo_id36 = to_base36(idn)
        root = await self._client.request('POST', f'/api/mod/conversations/{convo_id36}/archive')
        return load_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            client=self._client,
        )

    async def unarchive(self, idn: int) -> ConversationAggregate:
        convo_id36 = to_base36(idn)
        root = await self._client.request('POST', f'/api/mod/conversations/{convo_id36}/unarchive')
        return load_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            client=self._client,
        )

    async def approve_user(self, idn: int) -> UserDossierConversationAggregate:
        convo_id36 = to_base36(idn)
        root = await self._client.request('POST', f'/api/mod/conversations/{convo_id36}/approve')
        return load_user_dossier_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            root['user'],
            client=self._client,
        )

    async def unapprove_user(self, idn: int) -> UserDossierConversationAggregate:
        convo_id36 = to_base36(idn)
        root = await self._client.request('POST', f'/api/mod/conversations/{convo_id36}/disapprove')
        return load_user_dossier_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            root['user'],
            client=self._client,
        )

    async def mute_user_3d(self, idn: int) -> UserDossierConversationAggregate:
        convo_id36 = to_base36(idn)
        root = await self._client.request('POST', f'/api/mod/conversations/{convo_id36}/mute', data={'num_hours': '72'})
        return load_user_dossier_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            root['user'],
            client=self._client,
        )

    async def mute_user_7d(self, idn: int) -> UserDossierConversationAggregate:
        convo_id36 = to_base36(idn)
        root = await self._client.request('POST', f'/api/mod/conversations/{convo_id36}/mute', data={'num_hours': '168'})
        return load_user_dossier_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            root['user'],
            client=self._client,
        )

    async def mute_user_28d(self, idn: int) -> UserDossierConversationAggregate:
        convo_id36 = to_base36(idn)
        root = await self._client.request('POST', f'/api/mod/conversations/{convo_id36}/mute', data={'num_hours': '672'})
        return load_user_dossier_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            root['user'],
            client=self._client,
        )

    async def unmute_user(self, idn: int) -> UserDossierConversationAggregate:
        convo_id36 = to_base36(idn)
        root = await self._client.request('POST', f'/api/mod/conversations/{convo_id36}/unmute')
        return load_user_dossier_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            root['user'],
            client=self._client,
        )

    async def unban_user(self, idn: int) -> UserDossierConversationAggregate:
        convo_id36 = to_base36(idn)
        root = await self._client.request('POST', f'/api/mod/conversations/{convo_id36}/unban')
        return load_user_dossier_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            root['user'],
            client=self._client,
        )

    async def shorten_user_ban(self, idn: int, duration: int) -> UserDossierConversationAggregate:
        convo_id36 = to_base36(idn)
        root = await self._client.request('POST', f'/api/mod/conversations/{convo_id36}/temp_ban',
                data={'duration': str(duration)})
        return load_user_dossier_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            root['user'],
            client=self._client,
        )
