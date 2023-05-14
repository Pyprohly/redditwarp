
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....client_ASYNC import Client

from .text_ASYNC import Text
from .link_ASYNC import Link
from .image_ASYNC import Image
from .video_ASYNC import Video
from .gallery_ASYNC import Gallery
from .poll_ASYNC import Poll
from .cross_ASYNC import Cross

class Create:
    def __init__(self, client: Client) -> None:
        self._client = client

        self.text: Text = Text(client)
        ("""
            Create a text post.

            .. .PARAMETERS

            :param `str` sr:
                Name of the subreddit to submit the post to.
            :param `str` title:
                Title of the post.
            :param body:
                The body text of the post.

                Specify either markdown text or a richtext document.
            :type body: `Union`\\[`str`, `Mapping`\\[`str`, :class:`~.types.JSON_ro`]]
            :param `bool` reply_notifications:
                Receive inbox notifications for replies.
            :param `bool` spoiler:
                Mark as spoiler.
            :param `bool` nsfw:
                Mark as NSFW.
            :param `bool` oc:
                Mark as original content.
            :param `Optional[str]` collection_uuid:
                The UUID of a collection to add this post to a collection.
            :param `Optional[str]` flair_uuid:
                The UUID of a flair template to use.
            :param `Optional[str]` flair_text:
                Custom flair text.
            :param `Optional[str]` event_start:
                A datetime ISO 8601 string. E.g. `2018-09-11T12:00:00`.
            :param `Optional[str]` event_end:
                A datetime ISO 8601 string.
            :param `Optional[str]` event_tz:
                A timezone. E.g., `America/Los_Angeles`.

            .. .RETURNS

            :rtype: `None`
            :returns:
                For `_YIntOrStr` = `int`:
                    The integer ID of the newly created post.
                For `_YIntOrStr` = `str`:
                    The base 36 ID of the newly created post.

            .. .RAISES

            :raises redditwarp.exceptions.RedditError:
                + `USER_REQUIRED`:
                    There is no user context.
                + `BAD_SR_NAME`:
                    An empty string was specified for `sr`.
                + `SUBREDDIT_NOEXIST`:
                   - The specified subreddit does not exist.
                   - The specified subreddit is invalid.

                + `SUBREDDIT_NOTALLOWED`:
                   - The subreddit is restricted and you are not an approved user.
                   - You are banned from the subreddit.
                   - You are trying to submit an image or video post to a NSFW subreddit.

                   Note, quarantined subreddits can be posted to even if you haven't
                   yet opt-ed in to viewing its content.
                + `NO_TEXT`:
                    The `title` parameter was not specified, was blank, or contained only whitespace.
                + `JSON_PARSE_ERROR`:
                    Richtext was passed and it was not in the correct format.
                + `TOO_LONG`:
                   - The `title` parameter must be under 300 characters.
                   - The `body` parameter must be under 40000 characters.

                + `NO_SELFS`:
                    The subreddit doesn't accept text posts.
                + `USER_REQUIRED`:
                    There is no user context.
            :raises redditwarp.http.exceptions.StatusCodeException:
                + `404`:
                    The target subreddit is private or banned.
            """)
        self.link: Link = Link(client)
        ("""Create a link post.

            Behaves similarly to :meth:`.create_text_post`.

            .. .PARAMETERS

            :(parameters): Similar to :meth:`.create_text_post`.

            :param `str` url:
                A URL.
            :param `bool` resubmit:
                When the "Restrict how often the same link can be posted" content control
                setting is enabled, if a link with the same URL has already been submitted
                then an `ALREADY_SUB` API error would be returned unless this field is true.

            .. .RETURNS

            :(returns): Similar to :meth:`.create_text_post`.

            .. .RAISES

            :(raises): Similar to :meth:`.create_text_post`.

            :raises redditwarp.exceptions.RedditError:
                + `NO_URL`:
                    The `link` parameter was not specified, or the URL is invalid.
                + `ALREADY_SUB`:
                    The given link has already been submitted to the subreddit.
                    See parameter `resubmit`.
            """)
        self.image: Image = Image(client)
        ("""Create an image post.

            Behaves similarly to :meth:`.create_text_post`.

            .. .PARAMETERS

            :(parameters): Similar to :meth:`.create_text_post`.

            :param `str` link:
                A URL to an image.

            .. .RETURNS

            :(returns): Similar to :meth:`.create_text_post`.

            .. .RAISES

            :(raises): Similar to :meth:`.create_text_post`.
            """)
        self.video: Video = Video(client)
        ("""Create a video post.

            Behaves similarly to :meth:`.create_text_post`.

            .. .PARAMETERS

            :(parameters): Similar to :meth:`.create_text_post`.

            :param `str` link:
                A URL to a video.
            :param `str` thumbnail:
                A URL to an image to be used as a thumbnail for the video.
            :param `bool` vgif:
                Pass `True` to create a video GIF.

            .. .RETURNS

            :rtype: `None`

            .. .RAISES

            :(raises): Similar to :meth:`.create_text_post`.

            :raises redditwarp.exceptions.RedditError:
                + `MISSING_VIDEO_URLS`:
                    The `thumbnail` parameter was empty.
                + `NO_VIDEOS`:
                    The subreddit does not accept video posts.
            """)
        self.gallery: Gallery = Gallery(client)
        ("""Create a gallery post.

            Behaves similarly to :meth:`.create_text_post`.

            .. .PARAMETERS

            :(parameters): Similar to :meth:`.create_text_post`.

            :param items:
                A list of gallery items.
            :type items: `Sequence`\\[:class:`~.dtos.submission.GalleryItem`]

            .. .RETURNS

            :(returns): Similar to :meth:`.create_text_post`.

            .. .RAISES

            :(raises): Similar to :meth:`.create_text_post`.
            """)
        self.poll: Poll = Poll(client)
        ("""Create a poll post.

            Behaves similarly to :meth:`.create_text_post`.

            .. .PARAMETERS

            :(parameters): Similar to :meth:`.create_text_post`.

            :param `str` body:
            :param `Sequence[str]` options:
            :param `int` duration:
                The number of days the poll runs for.

                Valid values are 1 to 7. If a number is specified outside
                this range it is clamped within range.

                The UI default is 3 days.

            .. .RETURNS

            :(returns): Similar to :meth:`.create_text_post`.

            .. .RAISES

            :(raises): Similar to :meth:`.create_text_post`.
            """)
        self.cross: Cross = Cross(client)
        ("""Create a crosspost.

            Behaves similarly to :meth:`.create_text_post`.

            .. .PARAMETERS

            :(parameters): Similar to :meth:`.create_text_post`.

            :param `Union[int, str]` target:
                The ID of a submission.

            .. .RETURNS

            :(returns): Similar to :meth:`.create_text_post`.

            .. .RAISES

            :(raises): Similar to :meth:`.create_text_post`.
            """)
