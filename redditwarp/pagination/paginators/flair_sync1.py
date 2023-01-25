
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional, Sequence, Iterable
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ..paginator import MoreAvailablePaginator, Bidirectional, CursorPaginator
from ...models.flair import UserFlairAssociation
from ...model_loaders.flair import load_user_flair_association

class UserFlairAssociationPaginator(
        MoreAvailablePaginator[UserFlairAssociation], Bidirectional, CursorPaginator[UserFlairAssociation]):
    def __init__(self,
        client: Client,
        url: str,
        *,
        limit: Optional[int] = 1000,
    ) -> None:
        super().__init__()
        self.limit: Optional[int] = limit
        self.direction: bool = True
        self.client: Client = client
        self.url: str = url
        self._after: str = ''
        self._before: str = ''
        self._has_after: bool = True
        self._has_before: bool = True

    def get_cursor(self) -> str:
        return self._after if self.direction else self._before

    def set_cursor(self, value: str) -> None:
        if self.direction:
            self._after = value
        else:
            self._before = value

    def has_more_available(self) -> bool:
        return self._has_after if self.direction else self._has_before

    def set_has_more_available_flag(self, value: bool) -> None:
        if self.direction:
            self._has_after = value
        else:
            self._has_before = value

    def _generate_params(self) -> Iterable[tuple[str, str]]:
        if self.limit is not None:
            yield ('limit', str(self.limit))

        if self.direction:
            if self._after:
                yield ('after', self._after)
        else:
            if self._before:
                yield ('before', self._before)

    def _fetch_data(self) -> Any:
        params = dict(self._generate_params())
        data = self.client.request('GET', self.url, params=params)
        children = data['users']

        suggested_forward_cursor = data.get('after', '')
        suggested_backward_cursor = data.get('before', '')
        if children:
            self._after = suggested_forward_cursor
            self._before = suggested_backward_cursor
        self._has_after = bool(suggested_forward_cursor)
        self._has_before = bool(suggested_backward_cursor)

        return data

    def fetch(self) -> Sequence[UserFlairAssociation]:
        data = self._fetch_data()
        return [load_user_flair_association(d) for d in data['users']]
