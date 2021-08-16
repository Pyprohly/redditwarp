
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping, Optional, Sequence, Iterable
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.flair import UserFlairAssociation

from ..exceptions import MissingCursorException
from ...models.load.flair import load_user_flair_association
from ..bidirectional_cursor_paginator import BidirectionalCursorPaginator

class UserFlairAssociationPaginator(BidirectionalCursorPaginator[UserFlairAssociation]):
    def __init__(self,
        client: Client,
        uri: str,
        *,
        limit: Optional[int] = 1000,
    ):
        super().__init__()
        self.limit = limit
        self.client = client
        self.uri = uri

    def _generate_params(self) -> Iterable[tuple[str, Optional[str]]]:
        yield ('limit', str(self.limit))
        if self.direction:
            if not self.after and not self.has_after:
                raise MissingCursorException('after')
            yield ('after', self.after)
        else:
            if not self.before and not self.has_before:
                raise MissingCursorException('before')
            yield ('before', self.before)

    def _fetch_data(self) -> Mapping[str, Any]:
        params = dict(self._generate_params())
        data = self.client.request('GET', self.uri, params=params)
        children = data['users']
        after = data.get('after', '')
        before = data.get('before', '')

        if children:
            self.after = after
            self.before = before

        self.has_after = bool(after)
        self.has_before = bool(before)
        return data

    def fetch_next_result(self) -> Sequence[UserFlairAssociation]:
        data = self._fetch_data()
        return [load_user_flair_association(d) for d in data['users']]
