
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from .SYNC import SubredditProcedures

from ...util.base_conversion import to_base36
from ...exceptions import NoResultException

class Fetch:
    def __init__(self, outer: SubredditProcedures, client: Client) -> None:
        self._outer = outer
        self._client = client

    def __call__(self, id: int) -> object:
        id36 = to_base36(id)
        return self.by_id36(id36)

    def by_id36(self, id36: str) -> object:
        v = self._outer.get.by_id36(id36)
        if v is None:
            raise NoResultException('target not found')
        return v
