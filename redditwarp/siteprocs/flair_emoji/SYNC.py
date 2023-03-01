
from __future__ import annotations
from typing import TYPE_CHECKING, IO, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client

import os.path as op
from functools import cached_property

from ...models.flair_emoji import FlairEmojiUploadLease, SubredditFlairEmojis
from ...model_loaders.flair_emoji import load_flair_emoji_upload_lease, load_flair_emoji
from ...http.payload import guess_filename_mimetype

class FlairEmojiProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client

    def retrieve(self, sr: str) -> SubredditFlairEmojis:
        """Get a list of all flair emojis in a subreddit.

        .. .PARAMETERS

        :param `str` sr:

        .. .RETURNS

        :returns: A mapping from flair emoji name to
            :class:`~.models.flair_emoji.FlairEmoji`.
        :rtype: :class:`~.models.flair_emoji.SubredditFlairEmojis`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                The specified subreddit cannot be accessed.
            + `500`:
                The specified subreddit does not exist.
        """
        root = self._client.request('GET', f'/api/v1/{sr}/emojis/all')
        root = dict(root)
        reddit_emojis_root = root.pop('snoomojis')
        full_id36: str
        full_id36, subreddit_emojis_root = root.popitem()
        _, _, subreddit_id36 = full_id36.partition('_')
        subreddit_emojis = {name: load_flair_emoji(d, name) for name, d in subreddit_emojis_root.items()}
        reddit_emojis = {name: load_flair_emoji(d, name) for name, d in reddit_emojis_root.items()}
        all_emojis = {**subreddit_emojis, **reddit_emojis}
        return SubredditFlairEmojis(
            subreddit_emojis=subreddit_emojis,
            reddit_emojis=reddit_emojis,
            all_emojis=all_emojis,
            subreddit_id36=subreddit_id36,
        )

    class Create:
        def __init__(self, outer: FlairEmojiProcedures) -> None:
            self._client = outer._client

        def __call__(self,
            sr: str,
            name: str,
            file: IO[bytes],
            *,
            filepath: Optional[str] = None,
            mod_only: bool = False,
            user_enabled: bool = True,
            post_enabled: bool = True,
            timeout: float = 1000,
        ) -> None:
            upload_lease = self.upload(file, sr=sr, filepath=filepath, timeout=timeout)
            self.add(sr, upload_lease.s3_object_key, name,
                    user_enabled=user_enabled,
                    post_enabled=post_enabled,
                    mod_only=mod_only)

        def obtain_upload_lease(self,
            *,
            sr: str,
            filepath: str,
            mimetype: Optional[str] = None,
        ) -> FlairEmojiUploadLease:
            if mimetype is None:
                mimetype = guess_filename_mimetype(filepath)
            result = self._client.request('POST', f'/api/v1/{sr}/emoji_asset_upload_s3',
                    data={'filepath': filepath, 'mimetype': mimetype})
            return load_flair_emoji_upload_lease(result)

        def deposit_file(self,
            file: IO[bytes],
            upload_lease: FlairEmojiUploadLease,
            *,
            timeout: float = 1000,
        ) -> None:
            resp = self._client.http.request('POST', upload_lease.endpoint,
                    data=upload_lease.fields, files={'file': file}, timeout=timeout)
            resp.ensure_successful_status()

        def upload(self,
            file: IO[bytes],
            *,
            sr: str,
            filepath: Optional[str] = None,
            timeout: float = 1000,
        ) -> FlairEmojiUploadLease:
            if filepath is None:
                filepath = op.basename(getattr(file, 'name', ''))
                if not filepath:
                    raise ValueError("the `filepath` parameter must be explicitly specified if the file object has no `name` attribute.")
            upload_lease = self.obtain_upload_lease(sr=sr, filepath=filepath)
            self.deposit_file(file, upload_lease, timeout=timeout)
            return upload_lease

        def add(self,
            sr: str,
            name: str,
            s3_object_key: str,
            *,
            mod_only: bool = False,
            user_enabled: bool = True,
            post_enabled: bool = True,
        ) -> None:
            data = {
                's3_key': s3_object_key,
                'name': name,
                'user_flair_allowed': '01'[user_enabled],
                'post_flair_allowed': '01'[post_enabled],
                'mod_flair_only': '01'[mod_only],
            }
            self._client.request('POST', f'/api/v1/{sr}/emoji', data=data)

    create: cached_property[Create] = cached_property(Create)
    ("""
        Create a new flair emoji.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` name:
        :param `IO[bytes]` file:
        :param `Optional[str]` filepath:
        :param `bool` mod_only:
        :param `bool` post_enabled:
        :param `bool` user_enabled:
        :param `float` timeout:

        .. .RETURNS

        :rtype: `None`
        """)

    def set_permissions(self,
        sr: str,
        name: str,
        *,
        mod_only: bool = False,
        user_enabled: bool = True,
        post_enabled: bool = True,
    ) -> None:
        """Change emoji permissions.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` name:
        :param `bool` mod_only:
        :param `bool` user_enabled:
        :param `bool` post_enabled:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You do not have permission.
            + `404`:
                The specified emoji doesn't exist.
            + `500`:
               - The specified subreddit does not exist.
               - The specified emoji name was empty.
        """
        data = {
            'name': name,
            'mod_flair_only': '01'[mod_only],
            'user_flair_allowed': '01'[user_enabled],
            'post_flair_allowed': '01'[post_enabled],
        }
        self._client.request('POST', f'/api/v1/{sr}/emoji_permissions', data=data)

    def delete(self, sr: str, name: str) -> None:
        """Delete a flair emoji.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` name:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `400`:
               - The specified subreddit does not exist.
               - The specified emoji name was empty.
        """
        self._client.request('DELETE', f'/api/v1/{sr}/emoji/{name}')

    def enable_emojis_in_subreddit(self, sr: str) -> None:
        """Enable flair emojis in a subreddit.

        .. .PARAMETERS

        :param `str` sr:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You do not have permission.
            + `500`:
               - The specified subreddit does not exist.
               - The specified subreddit was empty.
        """
        data = {'subreddit': sr, 'enable': '1'}
        self._client.request('POST', '/api/enable_emojis_in_sr', data=data)

    def disable_emojis_in_subreddit(self, sr: str) -> None:
        """Disable flair emojis in a subreddit.

        .. .PARAMETERS

        :param `str` sr:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :(raises): Same as :meth:`.enable_emojis_in_subreddit`.
        """
        data = {'subreddit': sr, 'enable': '0'}
        self._client.request('POST', '/api/enable_emojis_in_sr', data=data)
