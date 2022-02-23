
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.comment_tree_SYNC import MoreCommentsTreeNode

from functools import cached_property

from ...util.base_conversion import to_base36
from ...models.load.comment_tree_SYNC import load_more_children
from .get_SYNC import Get
from .fetch_SYNC import Fetch

class CommentTreeProcedures:
    def __init__(self, client: Client):
        self._client = client
        self.get: Get = Get(self, client)
        self.fetch: Fetch = Fetch(self, client)

    class _more_children:
        def __init__(self, outer: CommentTreeProcedures):
            self._outer = outer
            self._client = outer._client

        def __call__(self,
            submission_id: int,
            child_ids: Iterable[int],
            *,
            sort: str = '',
            depth: Optional[int] = None,
            exact: bool = False,
        ) -> MoreCommentsTreeNode:
            return self.by_id36(
                to_base36(submission_id),
                (to_base36(x) for x in child_ids),
                sort=sort,
                depth=depth,
                exact=exact,
            )

        def by_id36(self,
            submission_id36: str,
            child_id36s: Iterable[str],
            *,
            sort: str = '',
            depth: Optional[int] = None,
            exact: bool = False,
        ) -> MoreCommentsTreeNode:
            def g() -> Iterable[tuple[str, str]]:
                yield ('link_id', 't3_' + submission_id36)
                yield ('children', ','.join(child_id36s))
                if sort:
                    yield ('sort', sort)
                if depth is not None:
                    yield ('depth', str(depth))
                if exact:
                    yield ('limit_children', '1')

            resp_data = self._client.request('GET', '/api/morechildren', params=dict(g()))
            return load_more_children(resp_data, self._client, submission_id36, sort)

    more_children: cached_property[_more_children] = cached_property(_more_children)
