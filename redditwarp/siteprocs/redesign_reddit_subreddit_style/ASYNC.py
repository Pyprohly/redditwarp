
from __future__ import annotations
from typing import TYPE_CHECKING, IO, Optional, Literal, Iterable, Protocol
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.subreddit_style_asset_upload_lease import SubredditStyleAssetUploadLease

import os.path as op
from functools import cached_property

from ...model_loaders.subreddit_style_asset_upload_lease import load_subreddit_style_asset_upload_lease
from ...http.payload import guess_filename_mimetype

class RedesignRedditSubredditStyleProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client

    class __BannerUploading:
        def __init__(self, outer: RedesignRedditSubredditStyleProcedures) -> None:
            self._client = outer._client

        async def __obtain_upload_lease(self,
            *,
            sr: str,
            filepath: str,
            mimetype: Optional[str] = None,
            imagetype: str,
        ) -> SubredditStyleAssetUploadLease:
            if mimetype is None:
                mimetype = guess_filename_mimetype(filepath)
            result = await self._client.request('POST', f'/api/v1/style_asset_upload_s3/{sr}',
                    data={'filepath': filepath, 'mimetype': mimetype, 'imagetype': imagetype})
            return load_subreddit_style_asset_upload_lease(result)

        async def obtain_banner_upload_lease(self,
            *,
            sr: str,
            filepath: str,
            mimetype: Optional[str] = None,
        ) -> SubredditStyleAssetUploadLease:
            return await self.__obtain_upload_lease(sr=sr, filepath=filepath, mimetype=mimetype, imagetype='bannerBackgroundImage')

        async def obtain_banner_overlay_upload_lease(self,
            *,
            sr: str,
            filepath: str,
            mimetype: Optional[str] = None,
        ) -> SubredditStyleAssetUploadLease:
            return await self.__obtain_upload_lease(sr=sr, filepath=filepath, mimetype=mimetype, imagetype='bannerPositionedImage')

        async def obtain_banner_overlay_hover_upload_lease(self,
            *,
            sr: str,
            filepath: str,
            mimetype: Optional[str] = None,
        ) -> SubredditStyleAssetUploadLease:
            return await self.__obtain_upload_lease(sr=sr, filepath=filepath, mimetype=mimetype, imagetype='secondaryBannerPositionedImage')

        async def obtain_mobile_banner_upload_lease(self,
            *,
            sr: str,
            filepath: str,
            mimetype: Optional[str] = None,
        ) -> SubredditStyleAssetUploadLease:
            return await self.__obtain_upload_lease(sr=sr, filepath=filepath, mimetype=mimetype, imagetype='mobileBannerImage')

        async def deposit_file(self,
            file: IO[bytes],
            upload_lease: SubredditStyleAssetUploadLease,
            *,
            timeout: float = 1000,
        ) -> None:
            resp = await self._client.http.request('POST', upload_lease.endpoint,
                    data=upload_lease.fields, files={'file': file}, timeout=timeout)
            resp.raise_for_status()

        class __ObtainUploadLeaseFunction(Protocol):
            async def __call__(self,
                *,
                sr: str,
                filepath: str,
                mimetype: Optional[str] = None,
            ) -> SubredditStyleAssetUploadLease: ...

        async def __upload(self,
            file: IO[bytes],
            *,
            sr: str,
            filepath: Optional[str] = None,
            timeout: float = 1000,
            obtain_upload_lease: __ObtainUploadLeaseFunction,
        ) -> SubredditStyleAssetUploadLease:
            if filepath is None:
                filepath = op.basename(getattr(file, 'name', ''))
                if not filepath:
                    raise ValueError("the `filepath` parameter must be explicitly specified if the file object has no `name` attribute.")
            upload_lease = await obtain_upload_lease(sr=sr, filepath=filepath)
            await self.deposit_file(file, upload_lease, timeout=timeout)
            return upload_lease

        async def upload_banner(self,
            file: IO[bytes],
            *,
            sr: str,
            filepath: Optional[str] = None,
            timeout: float = 1000,
        ) -> SubredditStyleAssetUploadLease:
            return await self.__upload(file=file, sr=sr, filepath=filepath, timeout=timeout, obtain_upload_lease=self.obtain_banner_upload_lease)

        async def upload_banner_overlay(self,
            file: IO[bytes],
            *,
            sr: str,
            filepath: Optional[str] = None,
            timeout: float = 1000,
        ) -> SubredditStyleAssetUploadLease:
            return await self.__upload(file=file, sr=sr, filepath=filepath, timeout=timeout, obtain_upload_lease=self.obtain_banner_overlay_upload_lease)

        async def upload_banner_overlay_hover(self,
            file: IO[bytes],
            *,
            sr: str,
            filepath: Optional[str] = None,
            timeout: float = 1000,
        ) -> SubredditStyleAssetUploadLease:
            return await self.__upload(file=file, sr=sr, filepath=filepath, timeout=timeout, obtain_upload_lease=self.obtain_banner_overlay_hover_upload_lease)

        async def upload_mobile_banner(self,
            file: IO[bytes],
            *,
            sr: str,
            filepath: Optional[str] = None,
            timeout: float = 1000,
        ) -> SubredditStyleAssetUploadLease:
            return await self.__upload(file=file, sr=sr, filepath=filepath, timeout=timeout, obtain_upload_lease=self.obtain_mobile_banner_upload_lease)

    banner_uploading: cached_property[__BannerUploading] = cached_property(__BannerUploading)

    async def configure_banner_settings(self,
        sr: str,
        *,
        banner_size: Optional[Literal['', 'small', 'medium', 'large']] = None,
        banner_background_color: Optional[str] = None,
        banner_image_url: Optional[str] = None,
        banner_image_display: Optional[Literal['', 'fill', 'tile']] = None,
        banner_overlay_image_url: Optional[str] = None,
        banner_overlay_image_position: Optional[Literal['', 'left', 'center', 'right']] = None,
        banner_overlay_hover_image_url: Optional[str] = None,
        mobile_banner_image_url: Optional[str] = None,
    ) -> None:
        def g() -> Iterable[tuple[str, str]]:
            if banner_size is not None:
                yield ('bannerHeight', banner_size)
            if banner_background_color is not None:
                yield ('bannerBackgroundColor', banner_background_color)
            if banner_image_url is not None:
                yield ('bannerBackgroundImage', banner_image_url)
            if banner_image_display is not None:
                v = {
                    '': '',
                    'fill': 'cover',
                    'tile': 'tiled',
                }[banner_image_display]
                yield ('bannerBackgroundImagePosition', v)
            if banner_overlay_image_url is not None:
                yield ('bannerPositionedImage', banner_overlay_image_url)
            if banner_overlay_image_position is not None:
                v = {
                    '': '',
                    'left': 'left',
                    'center': 'centered',
                    'right': 'right',
                }[banner_overlay_image_position]
                yield ('bannerPositionedImagePosition', v)
            if banner_overlay_hover_image_url is not None:
                yield ('secondaryBannerPositionedImage', banner_overlay_hover_image_url)
            if mobile_banner_image_url is not None:
                yield ('mobileBannerImage', mobile_banner_image_url)

        await self._client.request('PATCH', f'/api/v1/structured_styles/{sr}', data=dict(g()))
