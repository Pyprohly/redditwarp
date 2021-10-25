
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping, Optional, Sequence, Iterable
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ..bidirectional_cursor_paginator import BidirectionalCursorPaginator
from ..exceptions import MissingCursorException
from ...models.flair import UserFlairAssociation
from ...models.load.flair import load_user_flair_association

class UserFlairAssociationPaginator(BidirectionalCursorPaginator[UserFlairAssociation]):
    def __init__(self,
        client: Client,
        uri: str,
        *,
        limit: Optional[int] = 1000,
    ):
        super().__init__()
        self.limit: Optional[int] = limit
        self.client: Client = client
        self.uri: str = uri

    def _generate_params(self) -> Iterable[tuple[str, str]]:
        if self.limit is not None:
            yield ('limit', str(self.limit))

        if self.direction:
            if self.after:
                yield ('after', self.after)
            elif not self.has_after:
                raise MissingCursorException('after')
        else:
            if self.before:
                yield ('before', self.before)
            elif not self.has_before:
                raise MissingCursorException('before')

    def _next_data(self) -> Mapping[str, Any]:
        params = dict(self._generate_params())
        data = self.client.request('GET', self.uri, params=params)
        children = data['users']
        after = data.get('after', '')
        before = data.get('before', '')

        if children:
            self.after: str = after
            self.before: str = before

        self.has_after: bool = bool(after)
        self.has_before: bool = bool(before)
        return data

    def next_result(self) -> Sequence[UserFlairAssociation]:
        data = self._next_data()
        return [load_user_flair_association(d) for d in data['users']]
