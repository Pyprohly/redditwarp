
from __future__ import annotations
from typing import TYPE_CHECKING, IO, Mapping, Any, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client

from functools import cached_property

from ...models.flair_emoji import SubredditFlairEmojiInventory
from ...models.load.flair_emoji import load_flair_emoji
from ...http.payload import guess_mimetype_from_filename

class FlairEmoji:
    def __init__(self, client: Client):
        self._client = client

    def get_subreddit_emojis(self, sr: str) -> SubredditFlairEmojiInventory:
        root = self._client.request('GET', f'/api/v1/{sr}/emojis/all')
        reddit_emojis_root = root.pop('snoomojis')
        _full_id36: str
        _full_id36, subreddit_emojis_root = root.popitem()
        _, _, subreddit_id36 = _full_id36.partition('_')
        return SubredditFlairEmojiInventory(
            [load_flair_emoji(d, name) for name, d in subreddit_emojis_root.items()],
            [load_flair_emoji(d, name) for name, d in reddit_emojis_root.items()],
            subreddit_id36,
        )

    @cached_property
    class put:
        def __init__(self, outer: FlairEmoji) -> None:
            self._client = outer._client

        def __call__(self,
            sr: str,
            name: str,
            file: IO[bytes],
            *,
            filename: Optional[str] = None,
            mimetype: Optional[str] = None,
            post_enabled: bool = True,
            user_enabled: bool = True,
            mod_only: bool = False,
        ) -> None:
            if filename is None:
                filename = file.name
            upload_lease = self.obtain_upload_lease(sr, filename, mimetype)
            s3_key = self.upload(upload_lease, file)
            self.add(sr, s3_key, name,
                    post_enabled=post_enabled,
                    user_enabled=user_enabled,
                    mod_only=mod_only)

        def obtain_upload_lease(self, sr: str, filename: str, mimetype: Optional[str] = None) -> Mapping[str, Any]:
            if mimetype is None:
                mimetype = guess_mimetype_from_filename(filename)
            result = self._client.request('POST', f'/api/v1/{sr}/emoji_asset_upload_s3',
                    data={'filepath': filename, 'mimetype': mimetype})
            return result['s3UploadLease']

        def upload(self, upload_lease: Mapping[str, Any], file: IO[bytes]) -> str:
            bucket_server_url = 'https:' + upload_lease['action']
            data = {field['name']: field['value'] for field in upload_lease['fields']}
            files = {'file': file}
            session = self._client.http.session
            req = session.make_request('POST', bucket_server_url, data=data, files=files)
            resp = session.send(req)
            resp.raise_for_status()
            return upload_lease['fields']['key']

        def add(self, sr: str, s3_key: str, name: str, *,
                post_enabled: bool = True,
                user_enabled: bool = True,
                mod_only: bool = False) -> None:
            data = {
                's3_key': s3_key,
                'name': name,
                'post_flair_allowed': '01'[post_enabled],
                'user_flair_allowed': '01'[user_enabled],
                'mod_flair_only': '01'[mod_only],
            }
            self._client.request('POST', f'/api/v1/{sr}/emoji', data=data)
