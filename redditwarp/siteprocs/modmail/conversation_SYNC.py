
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Iterable
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_calling_iterator import CallChunkCallingIterator
from ...iterators.call_chunk_chaining_iterator import CallChunkChainingIterator
from ...iterators.call_chunk import CallChunk
from ...models.modmail_SYNC import (
    ConversationInfo,
    Message,
    ConversationAggregate,
    UserDossierConversationAggregate,
    OptionalUserDossierConversationAggregate,
)
from ...model_loaders.modmail_SYNC import (
    load_conversation_info,
    load_message,
    load_conversation_aggregate,
    load_user_dossier_conversation_aggregate,
    load_optional_user_dossier_conversation_aggregate,
)

class ConversationProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client

    def fetch(self, idn: int, *, mark_read: bool = False) -> OptionalUserDossierConversationAggregate:
        """Get a conversation.

        .. .PARAMETERS

        :param `int` idn:
            Conversation ID.
        :param `bool` mark_read:
            Mark retrieved conversations as read.

            Default: false.

        .. .RETURNS

        :rtype: :class:`~.models.modmail_SYNC.OptionalUserDossierConversationAggregate`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `SUBREDDIT_NO_ACCESS`:
                The subreddit associated with the conversation is not moderated by you.
            + `CONVERSATION_NOT_FOUND`:
                The specified conversation does not exist.
        """
        convo_id36 = to_base36(idn)
        root = self._client.request('GET', f'/api/mod/conversations/{convo_id36}')
        return load_optional_user_dossier_conversation_aggregate(
            root['conversation'],
            root['messages'],
            root['modActions'],
            root['user'] or None,
            client=self._client,
        )

    def create(self, sr: str, to: str, subject: str, body: str, *, hidden: bool = False) -> tuple[ConversationInfo, Message]:
        """Get a conversation.

        .. .PARAMETERS

        :param `str` sr:
            The name of the subreddit in which to create the conversation for.
        :param `str` to:
            The modmail recipient name.

            To create a moderator conversation, specify an empty string value.

            If the specified user is a moderator of the subreddit, this parameter
            is ignored and an internal moderator conversation is created instead.
        :param `str` subject:
            A subject line for the conversation.
        :param `str` body:
            Markdown text.
        :param `bool` hidden:
            Expose your user name to the recipient.

            Default: false.

        .. .RETURNS

        :rtype: `tuple`\\[:class:`~.models.modmail_SYNC.ConversationInfo`, :class:`~.models.modmail_SYNC.Message`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `BAD_SR_NAME`:
                The specified subreddit was empty.
            + `SUBREDDIT_NOEXIST`:
                The specified subreddit does not exist.
            + `NO_TEXT`:
               - The `subject` was empty.
               - The `body` was empty.

            + `TOO_LONG`:
               - The value specified for `subject` must be 100 characters or fewer
                 (despite error message saying under 100).
               - The value specified for `body` must be 10000 characters or fewer
                 (despite error message saying under 10000).
        """
        data = {'srName': sr, 'to': to, 'subject': subject, 'body': body, 'isAuthorHidden': '01'[hidden]}
        root = self._client.request('POST', '/api/mod/conversations', data=data)
        conversation_data = root['conversation']
        conversation = load_conversation_info(conversation_data, self._client)
        message_id36 = conversation_data['objIds'][0]['id']
        message = load_message(root['messages'][message_id36], self._client)
        return (conversation, message)

    def reply(self, idn: int, body: str, *, hidden: bool = False, internal: bool = False) -> ConversationAggregate:
        """Create a new message on an existing conversation.

        .. .PARAMETERS

        :param `int` idn:
            Conversation ID.
        :param `str` body:
            Markdown text.
        :param `bool` hidden:
            Expose your user name to the recipient.

            Default: false.
        :param `bool` internal:
            Create a private moderator note.

            Default: false.

        .. .RETURNS

        :rtype: :class:`~.models.modmail_SYNC.ConversationAggregate`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `CONVERSATION_NOT_FOUND`:
                The specified conversation does not exist.
            + `SUBREDDIT_NO_ACCESS`:
                The subreddit associated with the conversation is not moderated by you.
            + `NO_TEXT`:
                The `body` was empty.
            + `TOO_LONG`:
                The value specified for `body` must be 10000 characters or fewer
                (despite error message saying under 10000).
        """
        data = {'body': body, 'isAuthorHidden': '01'[hidden], 'isInternal': '01'[internal]}
        convo_id36 = to_base36(idn)
        root = self._client.request('POST', f'/api/mod/conversations/{convo_id36}', data=data)
        conversation_data = root['conversation']
        messages_mapping_data = root['messages']
        mod_actions_mapping_data = conversation_data['modActions']
        return load_conversation_aggregate(
            conversation_data,
            messages_mapping_data,
            mod_actions_mapping_data,
            client=self._client,
        )

    def mark_read(self, idn: int) -> None:
        """Mark a conversation as read.

        .. .PARAMETERS

        :param `int` idn:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        data = {'conversationIds': to_base36(idn)}
        self._client.request('POST', '/api/mod/conversations/read', data=data)

    def bulk_mark_read(self, ids: Iterable[int]) -> CallChunkCallingIterator[None]:
        """Mark conversations as read.

        Any specified conversation that does not exist will be ignored.
        If any of the IDs refer to a conversation you do not have permission over,
        an `INVALID_CONVERSATION_ID` API error will occur and none of the conversations
        will be processed.

        .. .PARAMETERS

        :param `Iterable[int]` ids:

        .. .RETURNS

        :rtype: :class:`~.iterators.call_chunk_calling_iterator.CallChunkCallingIterator`\\[`None`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `INVALID_CONVERSATION_ID`:
                You do not have permission to mark as read one of the specified conversations.
                The operation is aborted and none of the items will be processed.
        """
        def mass_mark_read(ids: Sequence[int]) -> None:
            id36s = map(to_base36, ids)
            ids_str = ','.join(id36s)
            self._client.request('POST', '/api/mod/conversations/read', data={'conversationIds': ids_str})

        return CallChunkCallingIterator(CallChunk(mass_mark_read, chunk) for chunk in chunked(ids, 100))

    def mark_unread(self, idn: int) -> None:
        """Mark a conversation as unread.

        Behaves similarly to :meth:`.mark_read`.
        """
        data = {'conversationIds': to_base36(idn)}
        self._client.request('POST', '/api/mod/conversations/unread', data=data)

    def bulk_mark_unread(self, ids: Iterable[int]) -> CallChunkCallingIterator[None]:
        """Mark conversations as unread.

        Behaves similarly to :meth:`.bulk_mark_read`.
        """
        def mass_mark_unread(ids: Sequence[int]) -> None:
            id36s = map(to_base36, ids)
            ids_str = ','.join(id36s)
            self._client.request('POST', '/api/mod/conversations/unread', data={'conversationIds': ids_str})

        return CallChunkCallingIterator(CallChunk(mass_mark_unread, chunk) for chunk in chunked(ids, 100))

    def bulk_mark_all_read(self, mailbox: str, subrs: Iterable[str]) -> CallChunkChainingIterator[int]:
        """Mark all conversations across select mailboxes and subreddits as read.

        Specified subreddit names that do not exist will be ignored, but if none of
        the subreddits exist then a 500 HTTP error will occur. If any of the subreddits
        are not moderated by you then a `BAD_SR_NAME` API error will occur, and none of
        the conversations will be processed.

        .. .PARAMETERS

        :param `str` mailbox:
            Either: `all`, `appeals`, `notifications`, `inbox`, `filtered`, `inprogress`,
            `mod`, `archived`, `default`, `highlighted`, `join_requests`, `new`.

            Defaults to `all` if empty string.
        :param `Iterable[str]` subrs:
            Subreddit names.

        .. .RETURNS

        :rtype: :class:`~.iterators.call_chunk_chaining_iterator.CallChunkChainingIterator`\\[`int`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `INVALID_OPTION`
                The specified `mailbox` was invalid.
            + `BAD_SR_NAME`:
                One of the specified subreddits is not a subreddit you have access to.
        """
        def mass_mark_all_read(subrs: Sequence[str]) -> Sequence[int]:
            subrs_str = ','.join(subrs)
            data = {'state': mailbox, 'entity': subrs_str}
            root = self._client.request('POST', '/api/mod/conversations/bulk/read', data=data)
            return [int(id36, 36) for id36 in root['conversation_ids']]

        return CallChunkChainingIterator(CallChunk(mass_mark_all_read, chunk) for chunk in chunked(subrs, 100))

    def highlight(self, idn: int) -> ConversationAggregate:
        """Mark a conversation as highlighted.

        .. .PARAMETERS

        :params `int` idn:

        .. .RETURNS

        :rtype: :class:`~.models.modmail_SYNC.ConversationAggregate`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `CONVERSATION_NOT_FOUND`:
                The specified conversation does not exist.
            + `SUBREDDIT_NO_ACCESS`:
                The subreddit associated with the conversation is not moderated by you.
        """
        convo_id36 = to_base36(idn)
        root = self._client.request('POST', f'/api/mod/conversations/{convo_id36}/highlight')
        return load_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            client=self._client,
        )

    def unhighlight(self, idn: int) -> ConversationAggregate:
        """Unmark a conversation as highlighted.

        Behaves similarly to :meth:`.highlight`.
        """
        convo_id36 = to_base36(idn)
        root = self._client.request('DELETE', f'/api/mod/conversations/{convo_id36}/highlight')
        return load_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            client=self._client,
        )

    def archive(self, idn: int) -> ConversationAggregate:
        """Archive a conversation.

        .. hint::
            Archiving a conversation moves it to the `archived` mailbox folder.

        .. .PARAMETERS

        :params `int` idn:

        .. .RETURNS

        :rtype: :class:`~.models.modmail_SYNC.ConversationAggregate`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `CONVERSATION_NOT_FOUND`:
                The specified conversation does not exist.
            + `INVALID_MOD_PERMISSIONS`:
                The subreddit associated with the conversation is not moderated by you.
        """
        convo_id36 = to_base36(idn)
        root = self._client.request('POST', f'/api/mod/conversations/{convo_id36}/archive')
        return load_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            client=self._client,
        )

    def unarchive(self, idn: int) -> ConversationAggregate:
        """Unmark a conversation as highlighted.

        Behaves similarly to :meth:`.highlight`.
        """
        convo_id36 = to_base36(idn)
        root = self._client.request('POST', f'/api/mod/conversations/{convo_id36}/unarchive')
        return load_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            client=self._client,
        )

    def approve_user(self, idn: int) -> UserDossierConversationAggregate:
        """Approve the user associated with a conversation.

        .. .PARAMETERS

        :params `int` idn:

        .. .RETURNS

        :rtype: :class:`~.models.modmail_SYNC.UserDossierConversationAggregate`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `CONVERSATION_NOT_FOUND`:
                The specified conversation does not exist.
            + `INVALID_MOD_PERMISSIONS`:
                The subreddit associated with the conversation is not moderated by you.
            + `CANT_RESTRICT_MODERATOR`:
                There is no user associated with the conversation.
        """
        convo_id36 = to_base36(idn)
        root = self._client.request('POST', f'/api/mod/conversations/{convo_id36}/approve')
        return load_user_dossier_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            root['user'],
            client=self._client,
        )

    def unapprove_user(self, idn: int) -> UserDossierConversationAggregate:
        """Unapprove the user associated with a conversation.

        Behaves similarly to :meth:`.approve_user`.
        """
        convo_id36 = to_base36(idn)
        root = self._client.request('POST', f'/api/mod/conversations/{convo_id36}/disapprove')
        return load_user_dossier_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            root['user'],
            client=self._client,
        )

    def mute_user_3d(self, idn: int) -> UserDossierConversationAggregate:
        """Mute the user associated with a conversation for 3 days.

        .. .PARAMETERS

        :params `int` idn:

        .. .RETURNS

        :rtype: :class:`~.models.modmail_SYNC.UserDossierConversationAggregate`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `CONVERSATION_NOT_FOUND`:
                The specified conversation does not exist.
            + `INVALID_MOD_PERMISSIONS`:
                The subreddit associated with the conversation is not moderated by you.
            + `CANT_RESTRICT_MODERATOR`:
                There is no user associated with the conversation.
        """
        convo_id36 = to_base36(idn)
        root = self._client.request('POST', f'/api/mod/conversations/{convo_id36}/mute', data={'num_hours': '72'})
        return load_user_dossier_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            root['user'],
            client=self._client,
        )

    def mute_user_7d(self, idn: int) -> UserDossierConversationAggregate:
        """Mute the user associated with a conversation for 7 days.

        Behaves similarly to :meth:`.mute_user_3d`.
        """
        convo_id36 = to_base36(idn)
        root = self._client.request('POST', f'/api/mod/conversations/{convo_id36}/mute', data={'num_hours': '168'})
        return load_user_dossier_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            root['user'],
            client=self._client,
        )

    def mute_user_28d(self, idn: int) -> UserDossierConversationAggregate:
        """Mute the user associated with a conversation for 28 days.

        Behaves similarly to :meth:`.mute_user_3d`.
        """
        convo_id36 = to_base36(idn)
        root = self._client.request('POST', f'/api/mod/conversations/{convo_id36}/mute', data={'num_hours': '672'})
        return load_user_dossier_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            root['user'],
            client=self._client,
        )

    def unmute_user(self, idn: int) -> UserDossierConversationAggregate:
        """Unmute the user associated with a conversation.

        Behaves similarly to :meth:`.mute_user_3d`.
        """
        convo_id36 = to_base36(idn)
        root = self._client.request('POST', f'/api/mod/conversations/{convo_id36}/unmute')
        return load_user_dossier_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            root['user'],
            client=self._client,
        )

    def shorten_user_ban(self, idn: int, duration: int) -> UserDossierConversationAggregate:
        """Switch a permanent ban to a temporary one of the user associated with a conversation.

        If the user is not permanently banned, an API error will be raised.

        .. .PARAMETERS

        :param `int` idn:
        :param `int` duration:
            The number of days the temporary ban should last.

            Specify an integer from 1 to 999.

            The UI has the options: 1, 3, 7, or 28 days.

        .. .RETURNS

        :rtype: :class:`~.models.modmail_SYNC.UserDossierConversationAggregate`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `CONVERSATION_NOT_FOUND`:
                The specified conversation does not exist.
            + `INVALID_MOD_PERMISSIONS`:
                The subreddit associated with the conversation is not moderated by you.
            + `CANT_RESTRICT_MODERATOR`:
                There is no user associated with the conversation.
            + `Participant must be banned.`:
                The user associated with the conversation is not banned from the subreddit.
            + `Participant must be banned permanently.`:
                The user associated with the conversation is not permanently banned from the subreddit.
            + `BAD_NUMBER`:
                The number specified by the `duration` parameter was not in range.
        """
        convo_id36 = to_base36(idn)
        root = self._client.request('POST', f'/api/mod/conversations/{convo_id36}/temp_ban',
                data={'duration': str(duration)})
        return load_user_dossier_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            root['user'],
            client=self._client,
        )

    def unban_user(self, idn: int) -> UserDossierConversationAggregate:
        """Unban the user associated with a conversation from the subreddit.

        .. .PARAMETERS

        :param `int` idn:

        .. .RETURNS

        :rtype: :class:`~.models.modmail_SYNC.UserDossierConversationAggregate`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `CONVERSATION_NOT_FOUND`:
                The specified conversation does not exist.
            + `INVALID_MOD_PERMISSIONS`:
                The subreddit associated with the conversation is not moderated by you.
            + `CANT_RESTRICT_MODERATOR`:
                There is no user associated with the conversation.
        """
        convo_id36 = to_base36(idn)
        root = self._client.request('POST', f'/api/mod/conversations/{convo_id36}/unban')
        return load_user_dossier_conversation_aggregate(
            root['conversations'],
            root['messages'],
            root['modActions'],
            root['user'],
            client=self._client,
        )
