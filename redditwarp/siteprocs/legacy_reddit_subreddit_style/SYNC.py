
from __future__ import annotations
from typing import TYPE_CHECKING, IO
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.stylesheet import StylesheetInfo

from ...model_loaders.stylesheet import load_stylesheet_info

class LegacyRedditSubredditStyleProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client

    def get_stylesheet(self, sr: str) -> StylesheetInfo:
        root = self._client.request('GET', '/about/stylesheet', params={'r': sr})
        return load_stylesheet_info(root['data'])

    def edit_stylesheet(self, sr: str, content: str, *, message: str) -> None:
        data = {'r': sr, 'op': 'save', 'stylesheet_contents': content, 'reason': message}
        self._client.request('POST', '/api/subreddit_stylesheet', data=data)

    def upload_stylesheet_image(self, sr: str, file: IO[bytes], name: str) -> None:
        self._client.request('POST', '/api/upload_sr_img',
                data={'r': sr, 'upload_type': 'img', 'name': name},
                files={'file': file})

    def delete_stylesheet_image(self, sr: str, name: str) -> None:
        self._client.request('POST', '/api/delete_sr_img', data={'r': sr, 'img_name': name})

    def set_icon(self, sr: str, file: IO[bytes]) -> None:
        self._client.request('POST', '/api/upload_sr_img',
                data={'r': sr, 'upload_type': 'header'},
                files={'file': file})

    def unset_icon(self, sr: str) -> None:
        self._client.request('POST', '/api/delete_sr_header', data={'r': sr})

    def set_mobile_icon(self, sr: str, file: IO[bytes]) -> None:
        self._client.request('POST', '/api/upload_sr_img',
                data={'r': sr, 'upload_type': 'icon'},
                files={'file': file})

    def unset_mobile_icon(self, sr: str) -> None:
        self._client.request('POST', '/api/delete_sr_icon', data={'r': sr})

    def set_mobile_banner(self, sr: str, file: IO[bytes]) -> None:
        self._client.request('POST', '/api/upload_sr_img',
                data={'r': sr, 'upload_type': 'banner'},
                files={'file': file})

    def unset_mobile_banner(self, sr: str) -> None:
        self._client.request('POST', '/api/delete_sr_banner', data={'r': sr})
