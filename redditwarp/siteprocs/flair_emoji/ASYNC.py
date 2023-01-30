
from __future__ import annotations
from typing import TYPE_CHECKING, IO, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client

import os.path as op
from functools import cached_property

from ...models.flair_emoji import FlairEmojiUploadLease, SubredditFlairEmojis
from ...model_loaders.flair_emoji import load_flair_emoji_upload_lease, load_flair_emoji
from ...http.payload import guess_filename_mimetype

class FlairEmojiProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client

    async def retrieve_subreddit_emojis(self, sr: str) -> SubredditFlairEmojis:
        root = await self._client.request('GET', f'/api/v1/{sr}/emojis/all')
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

        async def __call__(self,
            sr: str,
            name: str,
            file: IO[bytes],
            *,
            filepath: Optional[str] = None,
            post_enabled: bool = True,
            user_enabled: bool = True,
            mod_only: bool = False,
            timeout: float = 1000,
        ) -> None:
            upload_lease = await self.upload(file, sr=sr, filepath=filepath, timeout=timeout)
            await self.add(sr, upload_lease.s3_object_key, name,
                    post_enabled=post_enabled,
                    user_enabled=user_enabled,
                    mod_only=mod_only)

        async def obtain_upload_lease(self,
            *,
            sr: str,
            filepath: str,
            mimetype: Optional[str] = None,
        ) -> FlairEmojiUploadLease:
            if mimetype is None:
                mimetype = guess_filename_mimetype(filepath)
            result = await self._client.request('POST', f'/api/v1/{sr}/emoji_asset_upload_s3',
                    data={'filepath': filepath, 'mimetype': mimetype})
            return load_flair_emoji_upload_lease(result)

        async def deposit_file(self,
            file: IO[bytes],
            upload_lease: FlairEmojiUploadLease,
            *,
            timeout: float = 1000,
        ) -> None:
            resp = await self._client.http.request('POST', upload_lease.endpoint,
                    data=upload_lease.fields, files={'file': file}, timeout=timeout)
            resp.raise_for_status()

        async def upload(self,
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
            upload_lease = await self.obtain_upload_lease(sr=sr, filepath=filepath)
            await self.deposit_file(file, upload_lease, timeout=timeout)
            return upload_lease

        async def add(self,
            sr: str,
            name: str,
            s3_object_key: str,
            *,
            post_enabled: bool = True,
            user_enabled: bool = True,
            mod_only: bool = False,
        ) -> None:
            data = {
                's3_key': s3_object_key,
                'name': name,
                'post_flair_allowed': '01'[post_enabled],
                'user_flair_allowed': '01'[user_enabled],
                'mod_flair_only': '01'[mod_only],
            }
            await self._client.request('POST', f'/api/v1/{sr}/emoji', data=data)

    create: cached_property[Create] = cached_property(Create)

    async def set_emoji_permissions(self,
        sr: str,
        emoji_name: str,
        *,
        mod_only: bool = False,
        post_enabled: bool = True,
        user_enabled: bool = True,
    ) -> None:
        data = {
            'name': emoji_name,
            'mod_flair_only': '01'[mod_only],
            'post_flair_allowed': '01'[post_enabled],
            'user_flair_allowed': '01'[user_enabled],
        }
        await self._client.request('POST', f'/api/v1/{sr}/emoji_permissions', data=data)

    async def delete(self, sr: str, emoji_name: str) -> None:
        await self._client.request('DELETE', f'/api/v1/{sr}/emoji/{emoji_name}')

    async def set_custom_emoji_size(self, sr: str, size: Optional[tuple[int, int]]) -> None:
        data = None
        if size is not None:
            w, h = size
            data = {
                'width': str(w),
                'height': str(h),
            }
        await self._client.request('POST', f'/api/v1/{sr}/emoji_custom_size', data=data)

    async def enable_emojis_in_sr(self, sr: str) -> None:
        data = {'subreddit': sr, 'enable': '1'}
        await self._client.request('POST', '/api/enable_emojis_in_sr', data=data)

    async def disable_emojis_in_sr(self, sr: str) -> None:
        data = {'subreddit': sr, 'enable': '0'}
        await self._client.request('POST', '/api/enable_emojis_in_sr', data=data)
