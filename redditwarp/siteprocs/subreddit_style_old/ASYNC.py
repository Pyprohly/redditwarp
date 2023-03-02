
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
        """Get a subreddit's stylesheet information.

        This endpoint can be called without being a moderator of the target subreddit.
        You don't even have to be logged in.

        .. .PARAMETERS

        :param `str` sr:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `private`:
                You do not have access to the specified subreddit; it is private.
            + `banned`:
                You do not have access to the specified subreddit; it is banned.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `302`:
                The subreddit does not exist.
        """
        root = await self._client.request('GET', '/about/stylesheet', params={'r': sr})
        return load_stylesheet_info(root['data'])

    async def edit_stylesheet(self, sr: str, content: str, *, message: str = '') -> None:
        """Update a subreddit's stylesheet.

        The stylesheet can also be updated by editing the `config/stylesheet` wiki page.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` content:
        :param `str` message:
            A commit message.

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `private`:
                You do not have access to the specified subreddit; it is private.
            + `banned`:
                You do not have access to the specified subreddit; it is banned.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `404`:
                The subreddit does not exist.
        """
        data = {'r': sr, 'op': 'save', 'stylesheet_contents': content, 'reason': message}
        await self._client.request('POST', '/api/subreddit_stylesheet', data=data)

    async def add_stylesheet_image(self, sr: str, name: str, file: IO[bytes]) -> None:
        """Upload an image for use in the subreddit stylesheet.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` name:
            Must be a valid CSS identifier.
        :param `IO[bytes]` file:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `BAD_CSS_NAME`:
                The `name` parameter was not specified or was an invalid CSS identifier.
            + `IMAGE_ERROR`:
                The image file was invalid.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You do not have permission to upload an image to the specified subreddit.
        """
        payload = make_multipart({
            'r': sr,
            'upload_type': 'img',
            'name': name,
            'file': (file, 'file'),
        })
        await self._client.request('POST', '/api/upload_sr_img', payload=payload)

    async def remove_stylesheet_image(self, sr: str, name: str) -> None:
        """Delete an image from the subreddit's stylesheet custom image set.

        The image will no longer count against the subreddit's image limit,
        however the actual image data may still be accessible for an unspecified
        amount of time. If the image is currently referenced by the subreddit's
        stylesheet, that stylesheet will no longer validate and won't be
        submittable until the image reference is removed.

        If the specified image name does not exist, it is treated as a success.

        .. .PARAMETERS

        :param `str` sr:
        :param `str` name:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `500`:
                The `name` parameter was empty.
        """
        await self._client.request('POST', '/api/delete_sr_img', data={'r': sr, 'img_name': name})

    async def set_icon(self, sr: str, file: IO[bytes]) -> None:
        """Set the subreddit icon.

        .. .PARAMETERS

        :param `str` sr:
        :param `IO[bytes]` file:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `IMAGE_ERROR`:
                The image file was invalid.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You do not have permission to upload an image to the specified subreddit.
        """
        payload = make_multipart({
            'r': sr,
            'upload_type': 'header',
            'file': (file, 'file'),
        })
        await self._client.request('POST', '/api/upload_sr_img', payload=payload)

    async def unset_icon(self, sr: str) -> None:
        """Remove the subreddit's icon.

        .. .PARAMETERS

        :param `str` sr:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You do not have permission.
        """
        await self._client.request('POST', '/api/delete_sr_header', data={'r': sr})

    async def set_mobile_icon(self, sr: str, file: IO[bytes]) -> None:
        """Set the mobile icon.

        .. .PARAMETERS

        :param `str` sr:
        :param `IO[bytes]` file:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `IMAGE_ERROR`:
                The image file was invalid.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You do not have permission to upload an image to the specified subreddit.
        """
        payload = make_multipart({
            'r': sr,
            'upload_type': 'icon',
            'file': (file, 'file'),
        })
        await self._client.request('POST', '/api/upload_sr_img', payload=payload)

    async def unset_mobile_icon(self, sr: str) -> None:
        """Remove the mobile icon.

        .. .PARAMETERS

        :param `str` sr:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You do not have permission.
        """
        await self._client.request('POST', '/api/delete_sr_icon', data={'r': sr})

    async def set_mobile_banner(self, sr: str, file: IO[bytes]) -> None:
        """Set the mobile banner icon.

        .. .PARAMETERS

        :param `str` sr:
        :param `IO[bytes]` file:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `IMAGE_ERROR`:
                The image file was invalid.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You do not have permission to upload an image to the specified subreddit.
        """
        payload = make_multipart({
            'r': sr,
            'upload_type': 'banner',
            'file': (file, 'file'),
        })
        await self._client.request('POST', '/api/upload_sr_img', payload=payload)

    async def unset_mobile_banner(self, sr: str) -> None:
        """Remove the mobile banner icon.

        .. .PARAMETERS

        :param `str` sr:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You do not have permission.
        """
        await self._client.request('POST', '/api/delete_sr_banner', data={'r': sr})
