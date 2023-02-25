
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.comment_SYNC import Comment
    from .SYNC import CommentProcedures

from ...util.base_conversion import to_base36
from ...util.extract_id_from_url import extract_comment_id_from_url
from ...exceptions import NoResultException

class Fetch:
    def __init__(self, outer: CommentProcedures, client: Client) -> None:
        self._outer = outer
        self._client = client

    def __call__(self, idn: int) -> Comment:
        id36 = to_base36(idn)
        return self.by_id36(id36)

    def by_id36(self, id36: str) -> Comment:
        v = self._outer.get.by_id36(id36)
        if v is None:
            raise NoResultException('target not found')
        return v

    def by_url(self, url: str) -> Comment:
        return self(extract_comment_id_from_url(url))
