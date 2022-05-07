
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.submission_draft import Draft
    from ...models.submission_draft_ASYNC import DraftList

from ...model_loaders.submission_draft import load_public_draft
from ...model_loaders.submission_draft_ASYNC import load_draft_list
from ...util.base_conversion import to_base36

class DraftProcedures:
    def __init__(self, client: Client):
        self._client = client

    async def create_markdown_draft(self,
        *,
        public: Optional[bool] = None,
        subreddit_id: Optional[int] = None,
        title: Optional[str] = None,
        body: Optional[str] = None,
        reply_notifications: Optional[bool] = None,
        spoiler: Optional[bool] = None,
        nsfw: Optional[bool] = None,
        original_content: Optional[bool] = None,
        flair_text_override: Optional[str] = None,
    ) -> str:
        def g() -> Iterable[tuple[str, str]]:
            yield ('kind', 'markdown')
            if public is not None: yield ('is_public_link', '01'[public])
            if subreddit_id is not None: yield ('subreddit', 't5_' + to_base36(subreddit_id))
            if title is not None: yield ('title', title)
            if body is not None: yield ('body', body)
            if reply_notifications is not None: yield ('send_replies', '01'[reply_notifications])
            if spoiler is not None: yield ('spoiler', '01'[spoiler])
            if nsfw is not None: yield ('nsfw', '01'[nsfw])
            if original_content is not None: yield ('original_content', '01'[original_content])
            if flair_text_override is not None: yield ('flair_text', flair_text_override)

        root = await self._client.request('POST', '/api/v1/draft', data=dict(g()))
        return root['json']['data']['id']

    async def retrieve_my_drafts(self) -> DraftList:
        root = await self._client.request('GET', '/api/v1/drafts')
        return load_draft_list(root, self._client)

    async def read_public_draft(self, user: str, draft_uuid: str) -> Draft:
        uri = f"https://gateway.reddit.com/desktopapi/v1/draftpreviewpage/{user}/{draft_uuid}"
        root = await self._client.request('GET', uri)
        draft_data = root['drafts'][draft_uuid]
        return load_public_draft(draft_data)

    async def update_markdown_draft(self,
        uuid: str,
        *,
        public: Optional[bool] = None,
        subreddit_id: Optional[int] = None,
        title: Optional[str] = None,
        body: Optional[str] = None,
        reply_notifications: Optional[bool] = None,
        spoiler: Optional[bool] = None,
        nsfw: Optional[bool] = None,
        original_content: Optional[bool] = None,
        flair_text_override: Optional[str] = None,
    ) -> str:
        def g() -> Iterable[tuple[str, str]]:
            yield ('id', 'uuid')
            yield ('kind', 'markdown')
            if public is not None: yield ('is_public_link', '01'[public])
            if subreddit_id is not None: yield ('subreddit', 't5_' + to_base36(subreddit_id))
            if title is not None: yield ('title', title)
            if body is not None: yield ('body', body)
            if reply_notifications is not None: yield ('send_replies', '01'[reply_notifications])
            if spoiler is not None: yield ('spoiler', '01'[spoiler])
            if nsfw is not None: yield ('nsfw', '01'[nsfw])
            if original_content is not None: yield ('original_content', '01'[original_content])
            if flair_text_override is not None: yield ('flair_text', flair_text_override)

        root = await self._client.request('PUT', '/api/v1/draft', data=dict(g()))
        return root['json']['data']['id']

    async def delete(self, uuid: str) -> None:
        await self._client.request('DELETE', '/api/v1/draft', params={'draft_id': uuid})
