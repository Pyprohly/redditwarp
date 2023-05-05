
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional, TypeVar
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.comment_tree_SYNC import MoreCommentsTreeNode, SubmissionTreeNode

from ...util.base_conversion import to_base36
from .low_SYNC import Low

_YIntOrStr = TypeVar('_YIntOrStr', int, str)

class CommentTreeProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.low: Low = Low(self, client)
        ("""
            Low level calls for efficiency.
            """)

    def get(self,
        submission_id: _YIntOrStr,
        comment_id: Optional[_YIntOrStr] = None,
        *,
        sort: str = 'confidence',
        limit: Optional[int] = None,
        depth: Optional[int] = None,
        context: Optional[int] = None,
    ) -> Optional[SubmissionTreeNode]:
        """Get the comment tree for a submission.

        Behaves similarly to :meth:`.fetch`.

        Returns `None` instead of raises on `StatusCodeException(404)` and `RejectedResultException`.
        """
        # https://github.com/python/mypy/issues/4134
        submission_id36 = x if isinstance((x := submission_id), str) else to_base36(x)  # type: ignore[arg-type]
        # https://github.com/python/mypy/issues/4134
        comment_id36 = None if comment_id is None else (x if isinstance((x := comment_id), str) else to_base36(x))  # type: ignore[arg-type]
        return self.low.get(
            submission_id36,
            comment_id36,
            sort=sort,
            limit=limit,
            depth=depth,
            context=context,
        )

    def fetch(self,
        submission_id: _YIntOrStr,
        comment_id: Optional[_YIntOrStr] = None,
        *,
        sort: str = 'confidence',
        limit: Optional[int] = None,
        depth: Optional[int] = None,
        context: Optional[int] = None,
    ) -> SubmissionTreeNode:
        """Get the comment tree for a submission.

        .. .PARAMETERS

        :param `_YIntOrStr` submission_id:
            Submission ID.
        :param `Optional[_YIntOrStr]` comment_id:
            Optional comment ID to start the tree at that comment.
        :param `str` sort:
            Either: `confidence` ('best'), `top`, `new`, `controversial`, `old`, `random`, `qa`, `live`.

            If not given or not a valid sort value (including empty string), the default is the
            'sort comments by' preference of the logged in user. Otherwise, if there is no user
            context the default is `confidence`.
        :param `Optional[int]` limit:
            Limit the number of comments to retrieve.

            The effective default seems to be 200, and the max value appears to be 500.
        :param `Optional[int]` depth:
            The number of levels deep to retrieve comments for.

            A value of 0 is ignored.
            A value of 1 means to only retrieve top-level comments.
            A value of 2 means to retrieve comments one level deep.
            And so on.

            The maximum is 10, which is also the default.
            Any value higher than 10 is treated the same as 10.
        :param `Optional[int]` context:
            If `comment_id` is specified, the number of parent comments to include.

            Specify an integer from 0 to 8. Any number higher than 8 is treated the same as 8.

        .. .RETURNS

        :rtype: :class:`~.models.comment_tree_SYNC.SubmissionTreeNode`

        .. .RAISES

        :raises redditwarp.exceptions.RejectedResultException:
            When specifying a comment using the `comment_id` parameter and the returned
            comment list is empty, so the specified comment was not returned.

            This happens when the comment existed at one point but is no longer available
            anymore and no trace of the comment exists in the comment tree whatsoever.
            This can occur when a deleted comment has no replies but your program still
            has a reference to the comment and tried to retrieve it.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `404`:
               - The specified submission ID does not exist.
               - The specified comment ID does not exist or the comment belongs
                 to a submission other than the one specified.
        """
        # https://github.com/python/mypy/issues/4134
        submission_id36 = x if isinstance((x := submission_id), str) else to_base36(x)  # type: ignore[arg-type]
        # https://github.com/python/mypy/issues/4134
        comment_id36 = None if comment_id is None else (x if isinstance((x := comment_id), str) else to_base36(x))  # type: ignore[arg-type]
        return self.low.fetch(
            submission_id36,
            comment_id36,
            sort=sort,
            limit=limit,
            depth=depth,
            context=context,
        )

    def fetch_lenient(self,
        submission_id: _YIntOrStr,
        comment_id: Optional[_YIntOrStr] = None,
        *,
        sort: str = 'confidence',
        limit: Optional[int] = None,
        depth: Optional[int] = None,
        context: Optional[int] = None,
    ) -> SubmissionTreeNode:
        """Get the comment tree for a submission.

        Behaves similarly to :meth:`.fetch`.

        This method does the same thing as :meth:`.fetch` but doesn't reject
        with a `RejectedResultException` when the specified comment ID could
        not be retrieved.
        """
        # https://github.com/python/mypy/issues/4134
        submission_id36 = x if isinstance((x := submission_id), str) else to_base36(x)  # type: ignore[arg-type]
        # https://github.com/python/mypy/issues/4134
        comment_id36 = None if comment_id is None else (x if isinstance((x := comment_id), str) else to_base36(x))  # type: ignore[arg-type]
        return self.low.fetch(
            submission_id36,
            comment_id36,
            sort=sort,
            limit=limit,
            depth=depth,
            context=context,
        )

    def more_children(self,
        submission_id: _YIntOrStr,
        child_ids: Iterable[_YIntOrStr],
        *,
        sort: str = '',
        depth: Optional[int] = None,
        exact: bool = False,
    ) -> MoreCommentsTreeNode:
        """Retrieve comments omitted from a comment tree.

        When a comment tree is rendered, the most relevant comments are selected
        for display and the remaining comments are stubbed out with more-comment
        links: either 'load more comments' or 'continue this thread'. This procedure
        is used to retrieve the comments represented by the 'load more comments' stubs.

        You may only make one request at a time to this API endpoint.
        Higher concurrency will result in an error being returned.

        .. .PARAMETERS

        :param `_YIntOrStr` submission_id:
        :param `Iterable[_YIntOrStr]` child_ids:
            A list of comment IDs.
        :param `str` sort:
            Same as on :meth:`.fetch`.
        :param `Optional[int]` depth:
            Same as on :meth:`.fetch`.
        :param `bool` exact:
            If true, only return the children requested, and not their sub-comments.

            This is kind of the same as specifying `depth=1` but more-comment objects won't be present.

            If this is specified with the `depth` parameter, this parameter will take precedence.

        .. .RETURNS

        :rtype: :class:`~.models.comment_tree_SYNC.MoreCommentsTreeNode`

        .. .RAISES

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                The specified submission does not exist.
        """
        # https://github.com/python/mypy/issues/4134
        submission_id36 = x if isinstance((x := submission_id), str) else to_base36(x)  # type: ignore[arg-type]
        # https://github.com/python/mypy/issues/4134
        child_id36s = ((x if isinstance((x := i), str) else to_base36(x)) for i in child_ids)  # type: ignore[arg-type]
        return self.low.more_children(
            submission_id36,
            child_id36s,
            sort=sort,
            depth=depth,
            exact=exact,
        )
