
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable, Union, Mapping
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.submission_draft import SubmissionDraft
    from ...models.submission_draft_ASYNC import SubmissionDraftList
    from ...types import JSON_ro

import json

from ...model_loaders.submission_draft import load_public_submission_draft
from ...model_loaders.submission_draft_ASYNC import load_submission_draft_list
from ...util.base_conversion import to_base36

class DraftProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client

    async def retrieve(self) -> SubmissionDraftList:
        root = await self._client.request('GET', '/api/v1/drafts')
        return load_submission_draft_list(root, self._client)

    async def read_public_draft(self, user: str, draft_uuid: str) -> SubmissionDraft:
        url = f"https://gateway.reddit.com/desktopapi/v1/draftpreviewpage/{user}/{draft_uuid}"
        root = await self._client.request('GET', url)
        draft_data = root['drafts'][draft_uuid]
        return load_public_submission_draft(draft_data)

    async def create(self,
        *,
        public: Optional[bool] = None,
        subreddit_id: Optional[int] = None,
        title: Optional[str] = None,
        body: Optional[Union[str, Mapping[str, JSON_ro]]] = None,
        reply_notifications: Optional[bool] = None,
        spoiler: Optional[bool] = None,
        nsfw: Optional[bool] = None,
        oc: Optional[bool] = None,
        flair_uuid: Optional[str] = None,
        flair_text: Optional[str] = None,
    ) -> str:
        def g() -> Iterable[tuple[str, str]]:
            if body is not None:
                if isinstance(body, str):
                    yield ('kind', 'markdown')
                    yield ('body', body)
                else:
                    yield ('kind', 'richtext')
                    yield ('body', json.dumps(body))

            if public is not None: yield ('is_public_link', '01'[public])
            if subreddit_id is not None: yield ('subreddit', 't5_' + to_base36(subreddit_id))
            if title is not None: yield ('title', title)
            if reply_notifications is not None: yield ('send_replies', '01'[reply_notifications])
            if spoiler is not None: yield ('spoiler', '01'[spoiler])
            if nsfw is not None: yield ('nsfw', '01'[nsfw])
            if oc is not None: yield ('original_content', '01'[oc])
            if flair_uuid is not None: yield ('flair_id', flair_uuid)
            if flair_text is not None: yield ('flair_text', flair_text)

        root = await self._client.request('POST', '/api/v1/draft', data=dict(g()))
        return root['json']['data']['id']

    async def update(self,
        uuid: str,
        *,
        public: Optional[bool] = None,
        subreddit_id: Optional[int] = None,
        title: Optional[str] = None,
        body: Optional[Union[str, Mapping[str, JSON_ro]]] = None,
        reply_notifications: Optional[bool] = None,
        spoiler: Optional[bool] = None,
        nsfw: Optional[bool] = None,
        oc: Optional[bool] = None,
        flair_uuid: Optional[str] = None,
        flair_text: Optional[str] = None,
    ) -> str:
        def g() -> Iterable[tuple[str, str]]:
            yield ('id', 'uuid')

            if body is not None:
                if isinstance(body, str):
                    yield ('kind', 'markdown')
                    yield ('body', body)
                else:
                    yield ('kind', 'richtext')
                    yield ('body', json.dumps(body))

            if public is not None: yield ('is_public_link', '01'[public])
            if subreddit_id is not None: yield ('subreddit', 't5_' + to_base36(subreddit_id))
            if title is not None: yield ('title', title)
            if reply_notifications is not None: yield ('send_replies', '01'[reply_notifications])
            if spoiler is not None: yield ('spoiler', '01'[spoiler])
            if nsfw is not None: yield ('nsfw', '01'[nsfw])
            if oc is not None: yield ('original_content', '01'[oc])
            if flair_uuid is not None: yield ('flair_id', flair_uuid)
            if flair_text is not None: yield ('flair_text', flair_text)

        root = await self._client.request('PUT', '/api/v1/draft', data=dict(g()))
        return root['json']['data']['id']

    async def delete(self, uuid: str) -> None:
        await self._client.request('DELETE', '/api/v1/draft', params={'draft_id': uuid})
