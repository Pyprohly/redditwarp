
from __future__ import annotations
from typing import TYPE_CHECKING, IO, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client

from functools import cached_property

from ...models.flair_emoji import SubredditFlairEmojis
from ...models.load.flair_emoji import load_flair_emoji
from ...models.flair_emoji_upload_lease import FlairEmojiUploadLease
from ...models.load.flair_emoji_upload_lease import load_flair_emoji_upload_lease
from ...http.payload import guess_mimetype_from_filename

class FlairEmoji:
    def __init__(self, client: Client):
        self._client = client

    def get_subreddit_emojis(self, sr: str) -> SubredditFlairEmojis:
        root = self._client.request('GET', f'/api/v1/{sr}/emojis/all')
        root = dict(root)
        reddit_emojis_root = root.pop('snoomojis')
        _full_id36: str
        _full_id36, subreddit_emojis_root = root.popitem()
        _, _, subreddit_id36 = _full_id36.partition('_')
        return SubredditFlairEmojis(
            [load_flair_emoji(d, name) for name, d in subreddit_emojis_root.items()],
            [load_flair_emoji(d, name) for name, d in reddit_emojis_root.items()],
            subreddit_id36,
        )

    class _create:
        def __init__(self, outer: FlairEmoji) -> None:
            self._client = outer._client

        def __call__(self,
            sr: str,
            name: str,
            file: IO[bytes],
            *,
            post_enabled: bool = True,
            user_enabled: bool = True,
            mod_only: bool = False,
        ) -> None:
            upload_lease = self.upload(file, sr=sr)
            self.add(sr, upload_lease.fields['key'], name,
                    post_enabled=post_enabled,
                    user_enabled=user_enabled,
                    mod_only=mod_only)

        def obtain_upload_lease(self, filename: str, *, mimetype: Optional[str] = None, sr: str) -> FlairEmojiUploadLease:
            if mimetype is None:
                mimetype = guess_mimetype_from_filename(filename)
            result = self._client.request('POST', f'/api/v1/{sr}/emoji_asset_upload_s3',
                    data={'filepath': filename, 'mimetype': mimetype})
            return load_flair_emoji_upload_lease(result)

        def deposit_file(self, file: IO[bytes], upload_lease: FlairEmojiUploadLease) -> None:
            sess = self._client.http.session
            req = sess.make_request('POST', upload_lease.endpoint, data=upload_lease.fields, files={'file': file})
            resp = sess.send(req, timeout=-1)
            resp.raise_for_status()

        def upload(self, file: IO[bytes], *, sr: str) -> FlairEmojiUploadLease:
            upload_lease = self.obtain_upload_lease(file.name, sr=sr)
            self.deposit_file(file, upload_lease)
            return upload_lease

        def add(self, sr: str, s3_object_key: str, name: str, *,
                post_enabled: bool = True,
                user_enabled: bool = True,
                mod_only: bool = False) -> None:
            data = {
                's3_key': s3_object_key,
                'name': name,
                'post_flair_allowed': '01'[post_enabled],
                'user_flair_allowed': '01'[user_enabled],
                'mod_flair_only': '01'[mod_only],
            }
            self._client.request('POST', f'/api/v1/{sr}/emoji', data=data)

    create = cached_property(_create)

    def set_emoji_permissions(self,
        sr: str,
        emoji_name: str,
        *,
        mod_only: bool = False,
        user_enabled: bool = True,
        post_enabled: bool = True,
    ) -> None:
        data = {
            'name': emoji_name,
            'mod_flair_only': '01'[mod_only],
            'user_flair_allowed': '01'[user_enabled],
            'post_flair_allowed': '01'[post_enabled],
        }
        self._client.request('POST', f'/api/v1/{sr}/emoji_permissions', data=data)

    def delete(self, sr: str, emoji_name: str) -> None:
        self._client.request('DELETE', f'/api/v1/{sr}/emoji/{emoji_name}')

    def set_custom_emoji_size(self, sr: str, size: Optional[tuple[int, int]]) -> None:
        data = None
        if size is not None:
            w, h = size
            data = {
                'width': str(w),
                'height': str(h),
            }
        self._client.request('POST', f'/api/v1/{sr}/emoji_custom_size', data=data)

    def enable_emojis_in_sr(self, sr: str) -> None:
        data = {'subreddit': sr, 'enable': '1'}
        self._client.request('POST', '/api/enable_emojis_in_sr', data=data)

    def disable_emojis_in_sr(self, sr: str) -> None:
        data = {'subreddit': sr, 'enable': '0'}
        self._client.request('POST', '/api/enable_emojis_in_sr', data=data)
