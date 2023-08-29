
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Iterable, Union, TypeVar, Protocol, cast
if TYPE_CHECKING:
    from ...client_SYNC import Client

from functools import cached_property

from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_calling_iterator import CallChunkCallingIterator
from ...iterators.call_chunk_chaining_iterator import CallChunkChainingIterator
from ...iterators.call_chunk import CallChunk
from ...models.modmail_SYNC import ConversationAggregate
from ...model_loaders.modmail_SYNC import load_conversation_aggregate

_YIntOrStr = TypeVar('_YIntOrStr', int, str)

class ConversationProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client

    def fetch(self, idy: Union[int, str], *, mark_read: bool = False) -> ConversationAggregate:
        """Get a conversation.

        .. .PARAMETERS

        :param `Union[int, str]` idy:
            Conversation ID.
        :param `bool` mark_read:
            Mark retrieved conversations as read.

            Default: false.

        .. .RETURNS

        :rtype: :class:`~.models.modmail_SYNC.ConversationAggregate`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `SUBREDDIT_NO_ACCESS`:
                The subreddit associated with the conversation is not moderated by you.
            + `CONVERSATION_NOT_FOUND`:
                The specified conversation does not exist.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        root = self._client.request('GET', f'/api/mod/conversations/{id36}')
        return load_conversation_aggregate(root, client=self._client)

    def create_to_user(self, sr: str, to: str, subject: str, body: str, *, hidden: bool = False) -> ConversationAggregate:
        """Create a to-user conversation.

        .. .PARAMETERS

        :param `str` sr:
            The name of the subreddit in which to create the conversation for.
        :param `str` to:
            The modmail recipient name.

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

        :rtype: :class:`~.models.modmail_SYNC.ConversationAggregate`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `BAD_SR_NAME`:
                The specified source subreddit was empty.
            + `SUBREDDIT_NOEXIST`:
                The specified source subreddit does not exist.
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
        return load_conversation_aggregate(root, client=self._client)

    def create_to_subreddit(self, sr: str, to: str, subject: str, body: str) -> ConversationAggregate:
        """Create a to-subreddit conversation.

        .. .PARAMETERS

        :param `str` sr:
            The name of the subreddit in which to create the conversation for.
        :param `str` to:
            The target subreddit name.

            Specify an empty string to create an internal moderator conversation.
        :param `str` subject:
            A subject line for the conversation.
        :param `str` body:
            Markdown text.

        .. .RETURNS

        :rtype: :class:`~.models.modmail_SYNC.ConversationAggregate`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `BAD_SR_NAME`:
                The specified source subreddit was empty.
            + `SUBREDDIT_NOEXIST`:
                The specified source or target subreddit does not exist.
            + `NO_TEXT`:
               - The `subject` was empty.
               - The `body` was empty.

            + `TOO_LONG`:
               - The value specified for `subject` must be 100 characters or fewer
                 (despite error message saying under 100).
               - The value specified for `body` must be 10000 characters or fewer
                 (despite error message saying under 10000).
        """
        to = to and ('r/' + to)
        return self.create_to_user(sr, to, subject, body)

    def reply(self, idy: Union[int, str], body: str, *, hidden: bool = False, internal: bool = False) -> ConversationAggregate:
        """Create a new message on an existing conversation.

        .. .PARAMETERS

        :param `Union[int, str]` idy:
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
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        root = self._client.request('POST', f'/api/mod/conversations/{id36}', data=data)
        return load_conversation_aggregate(root, client=self._client)

    def mark_read(self, idy: Union[int, str]) -> None:
        """Mark a conversation as read.

        .. .PARAMETERS

        :param `Union[int, str]` idy:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `UNKNOWN_ERROR`:
                The string ID contained invalid characters.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {'conversationIds': id36}
        self._client.request('POST', '/api/mod/conversations/read', data=data)

    def bulk_mark_read(self, ids: Iterable[_YIntOrStr]) -> CallChunkCallingIterator[None]:
        """Mark conversations as read.

        Any specified conversation that does not exist will be ignored.
        If any of the IDs refer to a conversation you do not have permission over,
        an `INVALID_CONVERSATION_ID` API error will occur and none of the conversations
        will be processed.

        .. .PARAMETERS

        :param `Iterable[_YIntOrStr]` ids:

        .. .RETURNS

        :rtype: :class:`~.iterators.call_chunk_calling_iterator.CallChunkCallingIterator`\\[`None`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `INVALID_CONVERSATION_ID`:
                You do not have permission to mark as read one of the specified conversations.
                The operation is aborted and none of the items will be processed.
            + `UNKNOWN_ERROR`:
                The string ID contained invalid characters.
                The operation is aborted and none of the items will be processed.
        """
        def mass_mark_read(ids: Sequence[_YIntOrStr]) -> None:
            # https://github.com/python/mypy/issues/4134
            id36s = ((x if isinstance((x := i), str) else to_base36(x)) for i in ids)  # type: ignore[arg-type]
            ids_str = ','.join(id36s)
            self._client.request('POST', '/api/mod/conversations/read', data={'conversationIds': ids_str})

        return CallChunkCallingIterator(CallChunk[Sequence[_YIntOrStr], None](mass_mark_read, chunk) for chunk in chunked(ids, 100))

    def mark_unread(self, idy: Union[int, str]) -> None:
        """Mark a conversation as unread.

        Behaves similarly to :meth:`.mark_read`.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        data = {'conversationIds': id36}
        self._client.request('POST', '/api/mod/conversations/unread', data=data)

    def bulk_mark_unread(self, ids: Iterable[_YIntOrStr]) -> CallChunkCallingIterator[None]:
        """Mark conversations as unread.

        Behaves similarly to :meth:`.bulk_mark_read`.
        """
        def mass_mark_unread(ids: Sequence[_YIntOrStr]) -> None:
            # https://github.com/python/mypy/issues/4134
            id36s = ((x if isinstance((x := i), str) else to_base36(x)) for i in ids)  # type: ignore[arg-type]
            ids_str = ','.join(id36s)
            self._client.request('POST', '/api/mod/conversations/unread', data={'conversationIds': ids_str})

        return CallChunkCallingIterator(CallChunk[Sequence[_YIntOrStr], None](mass_mark_unread, chunk) for chunk in chunked(ids, 100))

    class BulkMarkAllRead:
        class GenericOverload(Protocol[_YIntOrStr]):
            def __call__(self, mailbox: str, subrs: Iterable[str]) -> CallChunkChainingIterator[_YIntOrStr]: ...

        def __init__(self, outer: ConversationProcedures) -> None:
            self._outer: ConversationProcedures = outer
            self._client: Client = outer._client

        def __call__(self, mailbox: str, subrs: Iterable[str]) -> CallChunkChainingIterator[int]:
            return self[int](mailbox, subrs)

        def __getitem__(self, key: type[_YIntOrStr]) -> GenericOverload[_YIntOrStr]:
            d = {
                int: self.y_int,
                str: self.y_str,
            }
            try:
                v = d[key]
            except KeyError as e:
                raise TypeError from e
            # https://github.com/python/mypy/issues/4177
            return cast("__class__.GenericOverload[_YIntOrStr]", cast(object, v))  # type: ignore[name-defined]

        def __helper(self, mailbox: str, subrs: Sequence[str]) -> Sequence[str]:
            subrs_str = ','.join(subrs)
            data = {'state': mailbox, 'entity': subrs_str}
            root = self._client.request('POST', '/api/mod/conversations/bulk/read', data=data)
            conversation_ids = root['conversation_ids']
            lst = []
            for i in conversation_ids:
                lhs, sep, rhs = i.partition('_')
                lst.append(rhs if sep else lhs)
            return lst

        def y_int(self, mailbox: str, subrs: Iterable[str]) -> CallChunkChainingIterator[int]:
            def mass_mark_all_read(subrs: Sequence[str]) -> Sequence[int]:
                l = self.__helper(mailbox, subrs)
                return [int(id36, 36) for id36 in l]

            return CallChunkChainingIterator(CallChunk[Sequence[str], Sequence[int]](mass_mark_all_read, chunk) for chunk in chunked(subrs, 100))

        def y_str(self, mailbox: str, subrs: Iterable[str]) -> CallChunkChainingIterator[str]:
            def mass_mark_all_read(subrs: Sequence[str]) -> Sequence[str]:
                return list(self.__helper(mailbox, subrs))

            return CallChunkChainingIterator(CallChunk[Sequence[str], Sequence[str]](mass_mark_all_read, chunk) for chunk in chunked(subrs, 100))

    bulk_mark_all_read: cached_property[BulkMarkAllRead] = cached_property(BulkMarkAllRead)
    ("""
        Mark all conversations across select mailboxes and subreddits as read.

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
        :returns:
            For `_YIntOrStr` = `int`:
                :class:`~.iterators.call_chunk_chaining_iterator.CallChunkChainingIterator`\\[`int`]
            For `_YIntOrStr` = `str`:
                :class:`~.iterators.call_chunk_chaining_iterator.CallChunkChainingIterator`\\[`str`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `INVALID_OPTION`
                The specified `mailbox` was invalid.
            + `BAD_SR_NAME`:
                One of the specified subreddits is not a subreddit you have access to.
        """)

    def highlight(self, idy: Union[int, str]) -> ConversationAggregate:
        """Mark a conversation as highlighted.

        .. .PARAMETERS

        :params `Union[int, str]` idy:

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
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        root = self._client.request('POST', f'/api/mod/conversations/{id36}/highlight')
        return load_conversation_aggregate(root, client=self._client)

    def unhighlight(self, idy: Union[int, str]) -> ConversationAggregate:
        """Unmark a conversation as highlighted.

        Behaves similarly to :meth:`.highlight`.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        root = self._client.request('DELETE', f'/api/mod/conversations/{id36}/highlight')
        return load_conversation_aggregate(root, client=self._client)

    def archive(self, idy: Union[int, str]) -> ConversationAggregate:
        """Archive a conversation.

        .. hint::
            Archiving a conversation moves it to the `archived` mailbox folder.

        .. .PARAMETERS

        :params `Union[int, str]` idy:

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
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        root = self._client.request('POST', f'/api/mod/conversations/{id36}/archive')
        return load_conversation_aggregate(root, client=self._client)

    def unarchive(self, idy: Union[int, str]) -> ConversationAggregate:
        """Unmark a conversation as highlighted.

        Behaves similarly to :meth:`.highlight`.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        root = self._client.request('POST', f'/api/mod/conversations/{id36}/unarchive')
        return load_conversation_aggregate(root, client=self._client)

    def approve_user(self, idy: Union[int, str]) -> ConversationAggregate:
        """Approve the user associated with a conversation.

        .. .PARAMETERS

        :params `Union[int, str]` idy:

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
            + `CANT_RESTRICT_MODERATOR`:
                There is no user associated with the conversation.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        root = self._client.request('POST', f'/api/mod/conversations/{id36}/approve')
        return load_conversation_aggregate(root, client=self._client)

    def unapprove_user(self, idy: Union[int, str]) -> ConversationAggregate:
        """Unapprove the user associated with a conversation.

        Behaves similarly to :meth:`.approve_user`.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        root = self._client.request('POST', f'/api/mod/conversations/{id36}/disapprove')
        return load_conversation_aggregate(root, client=self._client)

    def mute_user_3d(self, idy: Union[int, str]) -> ConversationAggregate:
        """Mute the user associated with a conversation for 3 days.

        .. .PARAMETERS

        :params `Union[int, str]` idy:

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
            + `CANT_RESTRICT_MODERATOR`:
                There is no user associated with the conversation.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        root = self._client.request('POST', f'/api/mod/conversations/{id36}/mute', data={'num_hours': '72'})
        return load_conversation_aggregate(root, client=self._client)

    def mute_user_7d(self, idy: Union[int, str]) -> ConversationAggregate:
        """Mute the user associated with a conversation for 7 days.

        Behaves similarly to :meth:`.mute_user_3d`.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        root = self._client.request('POST', f'/api/mod/conversations/{id36}/mute', data={'num_hours': '168'})
        return load_conversation_aggregate(root, client=self._client)

    def mute_user_28d(self, idy: Union[int, str]) -> ConversationAggregate:
        """Mute the user associated with a conversation for 28 days.

        Behaves similarly to :meth:`.mute_user_3d`.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        root = self._client.request('POST', f'/api/mod/conversations/{id36}/mute', data={'num_hours': '672'})
        return load_conversation_aggregate(root, client=self._client)

    def unmute_user(self, idy: Union[int, str]) -> ConversationAggregate:
        """Unmute the user associated with a conversation.

        Behaves similarly to :meth:`.mute_user_3d`.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        root = self._client.request('POST', f'/api/mod/conversations/{id36}/unmute')
        return load_conversation_aggregate(root, client=self._client)

    def shorten_user_ban(self, idy: Union[int, str], duration: int) -> ConversationAggregate:
        """Switch a permanent ban to a temporary one of the user associated with a conversation.

        If the user is not permanently banned, an API error will be raised.

        .. .PARAMETERS

        :param `Union[int, str]` idy:
        :param `int` duration:
            The number of days the temporary ban should last.

            Specify an integer from 1 to 999.

            The UI has the options: 1, 3, 7, or 28 days.

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
            + `CANT_RESTRICT_MODERATOR`:
                There is no user associated with the conversation.
            + `Participant must be banned.`:
                The user associated with the conversation is not banned from the subreddit.
            + `Participant must be banned permanently.`:
                The user associated with the conversation is not permanently banned from the subreddit.
            + `BAD_NUMBER`:
                The number specified by the `duration` parameter was not in range.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        root = self._client.request('POST', f'/api/mod/conversations/{id36}/temp_ban',
                data={'duration': str(duration)})
        return load_conversation_aggregate(root, client=self._client)

    def unban_user(self, idy: Union[int, str]) -> ConversationAggregate:
        """Unban the user associated with a conversation from the subreddit.

        .. .PARAMETERS

        :param `Union[int, str]` idy:

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
            + `CANT_RESTRICT_MODERATOR`:
                There is no user associated with the conversation.
        """
        id36 = x if isinstance((x := idy), str) else to_base36(x)
        root = self._client.request('POST', f'/api/mod/conversations/{id36}/unban')
        return load_conversation_aggregate(root, client=self._client)
