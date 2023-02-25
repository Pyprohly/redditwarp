
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.user_relationship import (
        UserRelationship,
        BannedSubredditUserRelationship,
    )
    from ...models.moderator_list import ModeratorListItem

from ...model_loaders.moderator_list import load_moderator_list_item
from ...model_loaders.user_relationship import load_user_relationship, load_banned_subreddit_user_relation

from .legacy_pull_users_SYNC import LegacyPullUsers

class Legacy:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.pull_users: LegacyPullUsers = LegacyPullUsers(client)
        ("""
            Get redditors that relate to a subreddit.

            .. .RAISES

            :(raises): Same as :meth:`.get_approved_user`.
            """)

    def list_moderators(self, sr: str) -> Sequence[ModeratorListItem]:
        """Get a list of moderators from a subreddit.

        This procedure doesn't work (403 HTTP error) if there is no user context.
        Use :meth:`~.siteprocs.moderation.pull_users_SYNC.PullUsers.moderators` instead.

        .. .RAISES

        :(raises): In addition to :meth:`.get_approved_user`:

        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
               - There is no user context.
               - The current user is banned from the subreddit.
        """
        root = self._client.request('GET', f'/r/{sr}/about/moderators')
        return [load_moderator_list_item(d) for d in root['data']['children']]


    def get_approved_user(self, sr: str, user: str) -> Optional[UserRelationship]:
        """Get information about an approved user in a subreddit.

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `private`:
                The target subreddit is private.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `302`:
                The target subreddit does not exist.
            + `403`:
                You don't have access to the subreddit.
            + `404`:
                The specified subreddit name is too long (over 21 characters)
                or contains invalid characters.
        """
        root = self._client.request('GET', f'/r/{sr}/about/contributors', params={'user': user})
        children = root['data']['children']
        return load_user_relationship(children[0]) if children else None

    def get_wiki_contributor(self, sr: str, user: str) -> Optional[UserRelationship]:
        """
        Behaves similarly to :meth:`.get_approved_user`.
        """
        root = self._client.request('GET', f'/r/{sr}/about/wikicontributors', params={'user': user})
        children = root['data']['children']
        return load_user_relationship(children[0]) if children else None

    def get_banned_user(self, sr: str, user: str) -> Optional[BannedSubredditUserRelationship]:
        """
        Behaves similarly to :meth:`.get_approved_user`.
        """
        root = self._client.request('GET', f'/r/{sr}/about/banned', params={'user': user})
        children = root['data']['children']
        return load_banned_subreddit_user_relation(children[0]) if children else None

    def get_muted_user(self, sr: str, user: str) -> Optional[UserRelationship]:
        """
        Behaves similarly to :meth:`.get_approved_user`.
        """
        root = self._client.request('GET', f'/r/{sr}/about/muted', params={'user': user})
        children = root['data']['children']
        return load_user_relationship(children[0]) if children else None

    def get_wiki_banned_user(self, sr: str, user: str) -> Optional[BannedSubredditUserRelationship]:
        """
        Behaves similarly to :meth:`.get_approved_user`.
        """
        root = self._client.request('GET', f'/r/{sr}/about/wikibanned', params={'user': user})
        children = root['data']['children']
        return load_banned_subreddit_user_relation(children[0]) if children else None
