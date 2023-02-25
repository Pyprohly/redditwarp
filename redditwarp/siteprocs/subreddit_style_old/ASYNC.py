
from __future__ import annotations
from typing import TYPE_CHECKING, IO
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.stylesheet import StylesheetInfo

from ...model_loaders.stylesheet import load_stylesheet_info
from ...http.payload import make_multipart

class SubredditStyleOldProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client

    async def get_stylesheet(self, sr: str) -> StylesheetInfo:
        root = await self._client.request('GET', '/about/stylesheet', params={'r': sr})
        return load_stylesheet_info(root['data'])

    async def edit_stylesheet(self, sr: str, content: str, *, message: str = '') -> None:
        data = {'r': sr, 'op': 'save', 'stylesheet_contents': content, 'reason': message}
        await self._client.request('POST', '/api/subreddit_stylesheet', data=data)

    async def add_stylesheet_image(self, sr: str, name: str, file: IO[bytes]) -> None:
        payload = make_multipart({
            'r': sr,
            'upload_type': 'img',
            'name': name,
            'file': (file, 'file'),
        })
        await self._client.request('POST', '/api/upload_sr_img', payload=payload)

    async def remove_stylesheet_image(self, sr: str, name: str) -> None:
        await self._client.request('POST', '/api/delete_sr_img', data={'r': sr, 'img_name': name})

    async def set_icon(self, sr: str, file: IO[bytes]) -> None:
        payload = make_multipart({
            'r': sr,
            'upload_type': 'header',
            'file': (file, 'file'),
        })
        await self._client.request('POST', '/api/upload_sr_img', payload=payload)

    async def unset_icon(self, sr: str) -> None:
        await self._client.request('POST', '/api/delete_sr_header', data={'r': sr})

    async def set_mobile_icon(self, sr: str, file: IO[bytes]) -> None:
        payload = make_multipart({
            'r': sr,
            'upload_type': 'icon',
            'file': (file, 'file'),
        })
        await self._client.request('POST', '/api/upload_sr_img', payload=payload)

    async def unset_mobile_icon(self, sr: str) -> None:
        await self._client.request('POST', '/api/delete_sr_icon', data={'r': sr})

    async def set_mobile_banner(self, sr: str, file: IO[bytes]) -> None:
        payload = make_multipart({
            'r': sr,
            'upload_type': 'banner',
            'file': (file, 'file'),
        })
        await self._client.request('POST', '/api/upload_sr_img', payload=payload)

    async def unset_mobile_banner(self, sr: str) -> None:
        await self._client.request('POST', '/api/delete_sr_banner', data={'r': sr})
