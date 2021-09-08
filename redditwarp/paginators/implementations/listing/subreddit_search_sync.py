
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable
if TYPE_CHECKING:
    from ....client_SYNC import Client

from ....models.subreddit_SYNC import Subreddit
from .mixins.sort_SYNC import Sort
from .user_pull_subreddits_sync import SubredditListingPaginator

class SearchSubredditsListingPaginator(
    Sort[Subreddit],
    SubredditListingPaginator,
):
    def __init__(self,
        client: Client,
        uri: str,
        query: str,
        show_users: bool = False,
    ):
        super().__init__(client, uri)
        self.query = query
        self.show_users = show_users

    def _generate_params(self) -> Iterable[tuple[str, Optional[str]]]:
        yield from super()._generate_params()
        yield ('q', self.query)
        if self.show_users:
            yield ('show_users', '1')
