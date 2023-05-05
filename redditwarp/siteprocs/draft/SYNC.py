
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable, Union, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_draft import SubmissionDraft
    from ...models.submission_draft_SYNC import SubmissionDraftList
    from ...types import JSON_ro

import json

from ...model_loaders.submission_draft import load_public_submission_draft
from ...model_loaders.submission_draft_SYNC import load_submission_draft_list
from ...util.base_conversion import to_base36

class DraftProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client

    def retrieve(self) -> SubmissionDraftList:
        """Retrieve the current user's drafts.

        .. .RETURNS

        :rtype: :class:`~.models.submission_draft_SYNC.SubmissionDraftList`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        root = self._client.request('GET', '/api/v1/drafts')
        return load_submission_draft_list(root, self._client)

    def read_public(self, user: str, uuid: str) -> SubmissionDraft:
        """Read a public draft.

        .. .PARAMETERS

        :param `str` user:
            User name.
        :param `str` uuid:
            Draft UUID.

        .. .RETURNS

        :rtype: `~.models.submission_draft.SubmissionDraft`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `FORBIDDEN`:
               - There is no user context.
               - The specified draft does not exist.
               - You do not have permission to view the draft.

            + `BAD_GATEWAY`:
                The specified ID is not a valid UUID.
            + `NOT_FOUND`:
                The specified draft could not be found.
        """
        url = f"https://gateway.reddit.com/desktopapi/v1/draftpreviewpage/{user}/{uuid}"
        root = self._client.request('GET', url)
        draft_data = root['drafts'][uuid]
        return load_public_submission_draft(draft_data)

    def create(self,
        *,
        body: Union[str, Mapping[str, JSON_ro]],
        public: Optional[bool] = None,
        subreddit_id: Optional[Union[int, str]] = None,
        title: Optional[str] = None,
        reply_notifications: Optional[bool] = None,
        spoiler: Optional[bool] = None,
        nsfw: Optional[bool] = None,
        oc: Optional[bool] = None,
        flair_uuid: Optional[str] = None,
        flair_text: Optional[str] = None,
    ) -> str:
        """Create a draft.

        .. .PARAMETERS

        :param body:
        :type body: `Union`\\[`str`, `Mapping`\\[`str`, :class:`~.types.JSON_ro`]]
        :param `Optional[bool]` public:
        :param `Optional[Union[int, str]]` subreddit_id:
        :param `Optional[str]` title:
        :param `Optional[bool]` reply_notifications:
        :param `Optional[bool]` spoiler:
        :param `Optional[bool]` nsfw:
        :param `Optional[bool]` oc:
        :param `Optional[str]` flair_uuid:
        :param `Optional[str]` flair_text:

        .. .RETURNS

        :returns: The UUID of the newly created draft.
        :rtype: `str`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
        """
        def g() -> Iterable[tuple[str, str]]:
            if isinstance(body, str):
                yield ('kind', 'markdown')
                yield ('body', body)
            else:
                yield ('kind', 'richtext')
                yield ('body', json.dumps(body))

            if public is not None: yield ('is_public_link', '01'[public])
            if subreddit_id is not None:
                id36 = x if isinstance((x := subreddit_id), str) else to_base36(x)
                yield ('subreddit', 't5_' + id36)
            if title is not None: yield ('title', title)
            if reply_notifications is not None: yield ('send_replies', '01'[reply_notifications])
            if spoiler is not None: yield ('spoiler', '01'[spoiler])
            if nsfw is not None: yield ('nsfw', '01'[nsfw])
            if oc is not None: yield ('original_content', '01'[oc])
            if flair_uuid is not None: yield ('flair_id', flair_uuid)
            if flair_text is not None: yield ('flair_text', flair_text)

        root = self._client.request('POST', '/api/v1/draft', data=dict(g()))
        return root['json']['data']['id']

    def replace(self,
        uuid: str,
        *,
        body: Union[str, Mapping[str, JSON_ro]],
        public: Optional[bool] = None,
        subreddit_id: Optional[Union[int, str]] = None,
        title: Optional[str] = None,
        reply_notifications: Optional[bool] = None,
        spoiler: Optional[bool] = None,
        nsfw: Optional[bool] = None,
        oc: Optional[bool] = None,
        flair_uuid: Optional[str] = None,
        flair_text: Optional[str] = None,
    ) -> None:
        """Update a draft.

        Every parameter should be specified otherwise their effective default will be used!
        """
        def g() -> Iterable[tuple[str, str]]:
            yield ('id', uuid)

            if isinstance(body, str):
                yield ('kind', 'markdown')
                yield ('body', body)
            else:
                yield ('kind', 'richtext')
                yield ('body', json.dumps(body))

            if public is not None: yield ('is_public_link', '01'[public])
            if subreddit_id is not None:
                id36 = x if isinstance((x := subreddit_id), str) else to_base36(x)
                yield ('subreddit', 't5_' + id36)
            if title is not None: yield ('title', title)
            if reply_notifications is not None: yield ('send_replies', '01'[reply_notifications])
            if spoiler is not None: yield ('spoiler', '01'[spoiler])
            if nsfw is not None: yield ('nsfw', '01'[nsfw])
            if oc is not None: yield ('original_content', '01'[oc])
            if flair_uuid is not None: yield ('flair_id', flair_uuid)
            if flair_text is not None: yield ('flair_text', flair_text)

        self._client.request('PUT', '/api/v1/draft', data=dict(g()))

    def delete(self, uuid: str) -> None:
        """Delete a draft.

        .. .PARAMETERS

        :param `str` uuid:

        .. .RETURNS

        :rtype: `None`

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `USER_REQUIRED`:
                There is no user context.
            + `VALIDATION_ERRORS`:
               - The specified draft does not exist.
               - The specified draft UUID is not valid.

            + `UNKNOWN_THRIFT_ERROR`:
                The specified draft no longer exists.
        """
        self._client.request('DELETE', '/api/v1/draft', params={'draft_id': uuid})
