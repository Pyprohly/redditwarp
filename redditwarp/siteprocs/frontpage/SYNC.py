
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.comment_SYNC import ExtraSubmissionFieldsComment

from .pull_SYNC import Pull

from ...paginators.paginator_chaining_iterator import PaginatorChainingIterator
from ...paginators.implementations.listing.p_user_pull_sync import ExtraSubmissionFieldsCommentListingPaginator

class FrontPage:
    def __init__(self, client: Client):
        self._client = client
        self.pull = Pull(client)

    def pull_new_comments(self, amount: Optional[int] = None) -> PaginatorChainingIterator[ExtraSubmissionFieldsCommentListingPaginator, ExtraSubmissionFieldsComment]:
        p = ExtraSubmissionFieldsCommentListingPaginator(self._client, '/comments')
        return PaginatorChainingIterator(p, amount)
