
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.message_SYNC import ComposedMessage

from functools import cached_property

from ...util.base_conversion import to_base36
from ...model_loaders.message_SYNC import load_composed_message, load_composed_message_thread
from .pulls_SYNC import Pulls

class MessageProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.pulls: Pulls = Pulls(client)
        ("""
            Pull messages.
            """)

    def get_thread(self, idn: int) -> Sequence[ComposedMessage]:
        """Get a message thread.

        Specifying the ID of any message in the same thread gives you the same list.

        .. .PARAMETERS

        :param `int` idn:
            Message ID.

        .. .RETURNS

        :rtype: `Sequence`\\[:class:`~.models.message_SYNC.ComposedMessage`]

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                The target message specified does not exist or
                you do not have permission to access it.
        """
        id36 = to_base36(idn)
        root = self._client.request('GET', f'/message/messages/{id36}')
        obj_data = root['data']['children'][0]['data']
        return load_composed_message_thread(obj_data, self._client)

    def send(self, to: str, subject: str, body: str) -> None:
        """Send a direct message to a user.

        .. .PARAMETERS

        :param `str` to:
            Name of user in which to send the message to.
        :param `str` subject:
            The subject of the message.
        :param `str` body:
            The body text of the message.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_USER`:
                The user specified by `to` was empty.
            + `NO_SUBJECT`:
                The subject specified by `subject` was empty.
            + `NO_TEXT`:
                The body text specified by `body` was empty.
            + `USER_DOESNT_EXIST`:
                The user specified by `to` does not exist.
            + `NOT_WHITELISTED_BY_USER_MESSAGE`:
                The target user has direct messages from strangers disabled.

                On old Reddit, this setting can be configured at `<https://old.reddit.com/prefs/blocked>`_
                by setting "Show private messages from" to "Only trusted users".
        """
        req_data = {
            'to': to,
            'subject': subject,
            'text': body,
        }
        self._client.request('POST', '/api/compose', data=req_data)

    def send_from_sr(self, sr: str, to: str, subject: str, body: str) -> None:
        """Send a direct message to a user on behalf of a subreddit.

        .. .PARAMETERS

        :param `str` sr:
            The name of a subreddit you moderate.
        :param `str` to:
            Name of user in which to send the message to.
        :param `str` subject:
            The subject of the message.
        :param `str` body:
            The body text of the message.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_USER`:
                The user specified by `to` was empty.
            + `NO_SUBJECT`:
                The subject specified by `subject` was empty.
            + `NO_TEXT`:
                The body text specified by `body` was empty.
            + `SUBREDDIT_NOEXIST`:
                The subreddit specified by `sr` does not exist.
            + `NO_SR_TO_SR_MESSAGE`:
                Both `sr` and `to` refer to subreddits.
                Subreddit to subreddit messages is not allowed.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                The current user is not a moderator of the specified subreddit.
        """
        req_data = {
            'from_sr': sr,
            'to': to,
            'subject': subject,
            'text': body,
        }
        self._client.request('POST', '/api/compose', data=req_data)

    def reply(self, idn: int, body: str) -> ComposedMessage:
        """Reply to a message

        .. .PARAMETERS

        :param `int` idn:
        :param `str` body:

        .. .RETURNS

        :returns: The newly created message.
        :rtype: :class:`~.models.message_SYNC.ComposedMessage`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `NO_TEXT`:
                The body text specified by `body` was empty.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                The specified message ID does not exist.
        """
        data = {
            'thing_id': 't4_' + to_base36(idn),
            'text': body,
            'return_rtjson': '1',
        }
        result = self._client.request('POST', '/api/comment', data=data)
        root = result['json']['data']['things'][0]['data']
        return load_composed_message(root, self._client)

    def delete(self, idn: int) -> None:
        """Delete a message.

        If the message specified by the ID doesn't exist, or is invalid,
        the action is treated as a success.

        .. .PARAMETERS

        :param `int` idn:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        self._client.request('POST', '/api/del_msg', data={'id': 't4_' + to_base36(idn)})

    def mark_read(self, idn: int) -> None:
        """Mark a message as read.

        Marking an already marked as read item is treated as a success.

        .. .PARAMETERS

        :param `int` idn:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `400`:
                The message specified by the ID doesn't exist or is invalid.
        """
        self._client.request('POST', '/api/read_message', data={'id': 't4_' + to_base36(idn)})

    def mark_unread(self, idn: int) -> None:
        """Mark a message as unread.

        Behaves similarly to :meth:`.mark_read`.
        """
        self._client.request('POST', '/api/unread_message', data={'id': 't4_' + to_base36(idn)})

    def mark_all_read(self) -> None:
        """Mark all messages as read.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        self._client.request('POST', '/api/read_all_messages')

    def mark_comment_read(self, idn: int) -> None:
        """Mark a comment message as read.

        Behaves similarly to :meth:`.mark_read`.
        """
        self._client.request('POST', '/api/read_message', data={'id': 't1_' + to_base36(idn)})

    def mark_comment_unread(self, idn: int) -> None:
        """Mark a comment message as unread.

        Behaves similarly to :meth:`.mark_read`.
        """
        self._client.request('POST', '/api/read_message', data={'id': 't1_' + to_base36(idn)})

    def collapse(self, idn: int) -> None:
        """Collapse a message.

        If the specified message does not exist or is valid,
        the action is treated as a success.

        .. .PARAMETERS

        :param `int` idn:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        self._client.request('POST', '/api/collapse_message', data={'id': 't4_' + to_base36(idn)})

    def uncollapse(self, idn: int) -> None:
        """Uncollapse a message.

        Behaves similarly to :meth:`.mark_read`.
        """
        self._client.request('POST', '/api/uncollapse_message', data={'id': 't4_' + to_base36(idn)})

    class BlockAuthor:
        def __init__(self, outer: MessageProcedures) -> None:
            self._client = outer._client

        def __call__(self, idn: int) -> None:
            self.of_message(idn)

        def of_message(self, idn: int) -> None:
            self._client.request('POST', '/api/block', data={'id': 't4_' + to_base36(idn)})

        def of_comment(self, idn: int) -> None:
            self._client.request('POST', '/api/block', data={'id': 't1_' + to_base36(idn)})

        def of_submission(self, idn: int) -> None:
            self._client.request('POST', '/api/block', data={'id': 't3_' + to_base36(idn)})

    block_author: cached_property[BlockAuthor] = cached_property(BlockAuthor)
    ("""
        Block the author of a message, comment, or submission.

        - Use :meth:`~.BlockAuthor.__call__` to block the author of a message.
        - Use :meth:`~.BlockAuthor.of_comment` to block the author of a comment.
        - Use :meth:`~.BlockAuthor.of_submission` to block the author of a submission.

        To block a user directly by ID or name, see
        :meth:`~.AccountProcedures.block_user_by_id` and :meth:`~.AccountProcedures.block_user_by_name`
        instead.

        .. .PARAMETERS

        :param `int` idn:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """)
