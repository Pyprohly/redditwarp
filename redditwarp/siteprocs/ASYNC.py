
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..client_ASYNC import Client

from .submission.ASYNC import SubmissionProcedures
from .comment.ASYNC import CommentProcedures
from .subreddit.ASYNC import SubredditProcedures
from .comment_tree.ASYNC import CommentTreeProcedures
from .front.ASYNC import FrontProcedures
from .user.ASYNC import UserProcedures
from .account.ASYNC import AccountProcedures
from .collection.ASYNC import CollectionProcedures
from .flair.ASYNC import FlairProcedures
from .flair_emoji.ASYNC import FlairEmojiProcedures
from .custom_feed.ASYNC import CustomFeedProcedures
from .live_thread.ASYNC import LiveThreadProcedures
from .message.ASYNC import MessageProcedures
from .moderation.ASYNC import ModerationProcedures
from .draft.ASYNC import DraftProcedures
from .misc.ASYNC import MiscProcedures
from .modmail.ASYNC import ModmailProcedures
from .widget.ASYNC import WidgetProcedures
from .wiki.ASYNC import WikiProcedures
from .subreddit_style_old.ASYNC import SubredditStyleOldProcedures
from .subreddit_style_new.ASYNC import SubredditStyleNewProcedures

class SiteProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.submission: SubmissionProcedures = SubmissionProcedures(client)
        self.comment: CommentProcedures = CommentProcedures(client)
        self.subreddit: SubredditProcedures = SubredditProcedures(client)
        self.comment_tree: CommentTreeProcedures = CommentTreeProcedures(client)
        self.front: FrontProcedures = FrontProcedures(client)
        self.user: UserProcedures = UserProcedures(client)
        self.account: AccountProcedures = AccountProcedures(client)
        self.collection: CollectionProcedures = CollectionProcedures(client)
        self.flair: FlairProcedures = FlairProcedures(client)
        self.flair_emoji: FlairEmojiProcedures = FlairEmojiProcedures(client)
        self.custom_feed: CustomFeedProcedures = CustomFeedProcedures(client)
        self.live_thread: LiveThreadProcedures = LiveThreadProcedures(client)
        self.message: MessageProcedures = MessageProcedures(client)
        self.moderation: ModerationProcedures = ModerationProcedures(client)
        self.draft: DraftProcedures = DraftProcedures(client)
        self.misc: MiscProcedures = MiscProcedures(client)
        self.modmail: ModmailProcedures = ModmailProcedures(client)
        self.widget: WidgetProcedures = WidgetProcedures(client)
        self.wiki: WikiProcedures = WikiProcedures(client)
        self.subreddit_style_old: SubredditStyleOldProcedures = SubredditStyleOldProcedures(client)
        self.subreddit_style_new: SubredditStyleNewProcedures = SubredditStyleNewProcedures(client)

    async def ping(self) -> None:
        await self._client.request('GET', '/api/v1/scopes', params={'scopes': 'read'})
