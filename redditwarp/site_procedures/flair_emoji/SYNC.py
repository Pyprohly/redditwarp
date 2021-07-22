
from __future__ import annotations
from typing import TYPE_CHECKING, IO, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client

from functools import cached_property

from ...models.flair_emoji import SubredditFlairEmojiInventory
from ...models.load.flair_emoji import load_flair_emoji
from ...models.flair_emoji_upload_lease import FlairEmojiUploadLease
from ...models.load.flair_emoji_upload_lease import load_flair_emoji_upload_lease
from ...http.payload import guess_mimetype_from_filename

class FlairEmoji:
    def __init__(self, client: Client):
        self._client = client

    def get_subreddit_emojis(self, sr: str) -> SubredditFlairEmojiInventory:
        root = self._client.request('GET', f'/api/v1/{sr}/emojis/all')
        root = dict(root)
        reddit_emojis_root = root.pop('snoomojis')
        _full_id36: str
        _full_id36, subreddit_emojis_root = root.popitem()
        _, _, subreddit_id36 = _full_id36.partition('_')
        return SubredditFlairEmojiInventory(
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

        def deposit(self, upload_lease: FlairEmojiUploadLease, file: IO[bytes]) -> None:
            sess = self._client.http.session
            req = sess.make_request('POST', upload_lease.endpoint, data=upload_lease.fields, files={'file': file})
            resp = sess.send(req)
            resp.raise_for_status()

        def upload(self, file: IO[bytes], *, sr: str) -> FlairEmojiUploadLease:
            upload_lease = self.obtain_upload_lease(file.name, sr=sr)
            self.deposit(upload_lease, file)
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
