
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable

if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.comment_tree_ASYNC import SubmissionTreeNode
    from .ASYNC import CommentTreeProcedures

from ...model_loaders.comment_tree_ASYNC import load_submission_tree_node, load_more_comments_tree_node
from ...exceptions import RejectedResultException
from ... import http
from ...models.comment_tree_ASYNC import MoreCommentsTreeNode

class Low:
    def __init__(self, outer: CommentTreeProcedures, client: Client) -> None:
        self._outer = outer
        self._client = client

    async def get(self,
        submission_id36: str,
        comment_id36: Optional[str] = None,
        *,
        sort: str = 'confidence',
        limit: Optional[int] = None,
        depth: Optional[int] = None,
        context: Optional[int] = None,
    ) -> Optional[SubmissionTreeNode]:
        try:
            return await self.fetch(
                submission_id36,
                comment_id36,
                sort=sort,
                limit=limit,
                depth=depth,
                context=context,
            )
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 404:
                return None
            raise
        except RejectedResultException:
            return None

    async def fetch(self,
        submission_id36: str,
        comment_id36: Optional[str] = None,
        *,
        sort: str = 'confidence',
        limit: Optional[int] = None,
        depth: Optional[int] = None,
        context: Optional[int] = None,
    ) -> SubmissionTreeNode:
        tree_node = await self.fetch_lenient(
            submission_id36,
            comment_id36,
            sort=sort,
            limit=limit,
            depth=depth,
            context=context,
        )

        if comment_id36 is not None and not tree_node.children:
            raise RejectedResultException('Specified comment not returned.')

        return tree_node

    async def fetch_lenient(self,
        submission_id36: str,
        comment_id36: Optional[str] = None,
        *,
        sort: str = 'confidence',
        limit: Optional[int] = None,
        depth: Optional[int] = None,
        context: Optional[int] = None,
    ) -> SubmissionTreeNode:
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

        root = await self._client.request('GET', '/comments/' + submission_id36, params=dict(g()))
        return load_submission_tree_node(root, self._client, sort)

    async def more_children(self,
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

        resp_data = await self._client.request('POST', '/api/morechildren', data=dict(g()))
        return load_more_comments_tree_node(resp_data, self._client, submission_id36, sort)
