
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.comment_tree_SYNC import MoreCommentsTreeNode, SubmissionTreeNode

from functools import cached_property

from ...util.base_conversion import to_base36
from ...model_loaders.comment_tree_SYNC import load_submission_tree_node, load_more_comments_tree_node
from .get_SYNC import Get
from .fetch_SYNC import Fetch

class CommentTreeProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.get: Get = Get(self, client)
        self.fetch: Fetch = Fetch(self, client)

    def fetch_lenient(self,
        submission_id: int,
        comment_id: Optional[int] = None,
        *,
        sort: str = 'confidence',
        limit: Optional[int] = None,
        depth: Optional[int] = None,
        context: Optional[int] = None,
    ) -> SubmissionTreeNode:
        submission_id36 = to_base36(submission_id)
        comment_id36 = None if comment_id is None else to_base36(comment_id)

        def g() -> Iterable[tuple[str, str]]:
            if comment_id36 is not None:
                yield ('comment', comment_id36)
            if sort:
                yield ('sort', sort)
            if limit is not None:
                yield ('limit', str(limit))
            if depth is not None:
                yield ('depth', str(depth))
            if context is not None:
                yield ('context', str(context))

        root = self._client.request('GET', '/comments/' + submission_id36, params=dict(g()))
        return load_submission_tree_node(root, self._client, sort)

    class _more_children:
        def __init__(self, outer: CommentTreeProcedures) -> None:
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

            resp_data = self._client.request('POST', '/api/morechildren', data=dict(g()))
            return load_more_comments_tree_node(resp_data, self._client, submission_id36, sort)

    more_children: cached_property[_more_children] = cached_property(_more_children)
