
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable, Any, TypeVar, Mapping
if TYPE_CHECKING:
    from ....client_ASYNC import Client

from ...async_paginator import HasMoreAsyncPaginator, CursorAsyncPaginator
from ....models.moderation_note import (
        ModerationNote,
        ModerationUserNote,
    )
from ....model_loaders.moderation_note import (
    load_moderation_note,
    load_moderation_user_note,
)


T = TypeVar('T', bound='ModerationNote')

class GBaseModerationNoteAsyncPaginator(HasMoreAsyncPaginator[T], CursorAsyncPaginator[T]):
    def __init__(self,
        client: Client,
        url: str = '/api/mod/notes',
        *,
        limit: Optional[int] = 100,
        cursor: str = '',
        subreddit: str,
        user: str,
        type: Optional[str] = None,
    ) -> None:
        super().__init__(limit=limit)
        self.client: Client = client
        ("")
        self.url: str = url
        ("")
        self._cursor: str = cursor
        self._has_next_page: bool = True
        self._subreddit: str = subreddit
        self._user: str = user
        self._type: Optional[str] = type

    def get_cursor(self) -> str:
        return self._cursor

    def set_cursor(self, value: str) -> None:
        self._cursor = value

    def has_more(self) -> bool:
        return self._has_next_page

    def set_has_more(self, value: bool) -> None:
        self._has_next_page = value

    def _generate_params(self) -> Iterable[tuple[str, str]]:
        if self.limit is not None:
            yield ('count', str(self.limit))

        if self._cursor:
            yield ('before', self._cursor)

        yield ('subreddit', self._subreddit)
        yield ('user', self._user)
        if self._type:
            yield ('filter', self._type)

    async def _fetch_data(self) -> Any:
        params = dict(self._generate_params())
        root = await self.client.request('GET', self.url, params=params)
        self._cursor = root['end_cursor']
        self._has_next_page = root['has_next_page']
        return root

    async def fetch(self) -> Sequence[T]:
        root = await self._fetch_data()
        mod_notes = root['mod_notes']
        return [self._load_mod_note(d) for d in mod_notes]

    def _load_mod_note(self, d: Mapping[str, Any]) -> T:
        raise NotImplementedError


class ModerationNoteAsyncPaginator(GBaseModerationNoteAsyncPaginator[ModerationNote]):
    def _load_mod_note(self, d: Mapping[str, Any]) -> ModerationNote:
        return load_moderation_note(d)

class ModerationUserNoteAsyncPaginator(GBaseModerationNoteAsyncPaginator[ModerationUserNote]):
    def __init__(self,
        client: Client,
        url: str = '/api/mod/notes',
        *,
        limit: Optional[int] = 100,
        cursor: str = '',
        subreddit: str,
        user: str,
        type: Optional[str] = None,
    ) -> None:
        if type != 'NOTE':
            raise ValueError('`type` must be `NOTE`')
        super().__init__(
            client=client,
            url=url,
            cursor=cursor,
            subreddit=subreddit,
            user=user,
            type=type,
        )

    def _load_mod_note(self, d: Mapping[str, Any]) -> ModerationUserNote:
        return load_moderation_user_note(d)
