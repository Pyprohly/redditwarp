
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, Optional, Sequence, cast
if TYPE_CHECKING:
    from ....client_SYNC import Client
    from ....models.flair import UserFlairAssociation

from ....api.load.flair import load_user_flair_association
from ..cursor_bidirectional_paginator import CursorBidirectionalPaginator

class FlairAssociationsPaginator(CursorBidirectionalPaginator[UserFlairAssociation]):
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

    def _get_params(self) -> Dict[str, str]:
        params: Dict[str, Optional[str]] = {
            'limit': str(self.limit),
        }
        if self.get_direction():
            params['after'] = self.forward_cursor
        else:
            params['before'] = self.backward_cursor
        remove_keys = [k for k, v in params.items() if v is None]
        for k in remove_keys: del params[k]
        return cast(Dict[str, str], params)

    def _fetch_data(self) -> Dict[str, Any]:
        params = self._get_params()
        recv = self.client.request('GET', self.uri, params=params)
        entries = recv['users']
        after = recv.get('after')
        before = recv.get('before')

        if entries:
            self.forward_cursor = after
            self.backward_cursor = before

        self.forward_available = bool(after)
        self.backward_available = bool(before)
        return recv

    def _fetch_result(self) -> Sequence[UserFlairAssociation]:
        data = self._fetch_data()
        return [load_user_flair_association(d) for d in data['users']]

    def next_result(self) -> Sequence[UserFlairAssociation]:
        self.resuming = False
        return self._fetch_result()
