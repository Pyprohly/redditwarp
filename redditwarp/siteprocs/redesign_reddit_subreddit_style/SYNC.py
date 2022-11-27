
from __future__ import annotations
from typing import TYPE_CHECKING, IO, Optional, Literal, Iterable
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.subreddit_style_asset_upload_lease import SubredditStyleAssetUploadLease

from functools import cached_property

from ...model_loaders.subreddit_style_asset_upload_lease import load_subreddit_style_asset_upload_lease
from ...http.payload import guess_mimetype_from_filename

class RedesignRedditSubredditStyleProcedures:
    def __init__(self, client: Client):
        self._client = client

    class _upload_banner:
        def __init__(self, outer: RedesignRedditSubredditStyleProcedures) -> None:
            self._client = outer._client

        def _obtain_upload_lease(self, *, sr: str, filename: str, mimetype: Optional[str] = None, imagetype: str) -> SubredditStyleAssetUploadLease:
            if mimetype is None:
                mimetype = guess_mimetype_from_filename(filename)
            result = self._client.request('POST', f'/api/v1/style_asset_upload_s3/{sr}',
                    data={'filepath': filename, 'mimetype': mimetype, 'imagetype': imagetype})
            return load_subreddit_style_asset_upload_lease(result)

        def obtain_banner_upload_lease(self, *, sr: str, filename: str, mimetype: Optional[str] = None) -> SubredditStyleAssetUploadLease:
            return self._obtain_upload_lease(sr=sr, filename=filename, mimetype=mimetype, imagetype='bannerBackgroundImage')

        def obtain_banner_overlay_upload_lease(self, *, sr: str, filename: str, mimetype: Optional[str] = None) -> SubredditStyleAssetUploadLease:
            return self._obtain_upload_lease(sr=sr, filename=filename, mimetype=mimetype, imagetype='bannerPositionedImage')

        def obtain_banner_overlay_hover_upload_lease(self, *, sr: str, filename: str, mimetype: Optional[str] = None) -> SubredditStyleAssetUploadLease:
            return self._obtain_upload_lease(sr=sr, filename=filename, mimetype=mimetype, imagetype='secondaryBannerPositionedImage')

        def obtain_mobile_banner_upload_lease(self, *, sr: str, filename: str, mimetype: Optional[str] = None) -> SubredditStyleAssetUploadLease:
            return self._obtain_upload_lease(sr=sr, filename=filename, mimetype=mimetype, imagetype='mobileBannerImage')

        def deposit_file(self, file: IO[bytes], upload_lease: SubredditStyleAssetUploadLease, *,
                timeout: float = 1000) -> None:
            resp = self._client.http.request('POST', upload_lease.endpoint, data=upload_lease.fields,
                    files={'file': file}, timeout=timeout)
            resp.raise_for_status()

        def upload_banner(self, file: IO[bytes], *, sr: str, timeout: float = 1000) -> SubredditStyleAssetUploadLease:
            upload_lease = self.obtain_banner_upload_lease(filename=file.name, sr=sr)
            self.deposit_file(file, upload_lease, timeout=timeout)
            return upload_lease

        def upload_banner_overlay(self, file: IO[bytes], *, sr: str, timeout: float = 1000) -> SubredditStyleAssetUploadLease:
            upload_lease = self.obtain_banner_overlay_upload_lease(filename=file.name, sr=sr)
            self.deposit_file(file, upload_lease, timeout=timeout)
            return upload_lease

        def upload_banner_overlay_hover(self, file: IO[bytes], *, sr: str, timeout: float = 1000) -> SubredditStyleAssetUploadLease:
            upload_lease = self.obtain_banner_overlay_hover_upload_lease(filename=file.name, sr=sr)
            self.deposit_file(file, upload_lease, timeout=timeout)
            return upload_lease

        def upload_mobile_banner(self, file: IO[bytes], *, sr: str, timeout: float = 1000) -> SubredditStyleAssetUploadLease:
            upload_lease = self.obtain_mobile_banner_upload_lease(filename=file.name, sr=sr)
            self.deposit_file(file, upload_lease, timeout=timeout)
            return upload_lease

    upload_banner: cached_property[_upload_banner] = cached_property(_upload_banner)

    def configure_banner_settings(self,
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

        self._client.request('PATCH', f'/api/v1/structured_styles/{sr}', data=dict(g()))
