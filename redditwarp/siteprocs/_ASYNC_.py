
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..client_ASYNC import Client

from .submission._ASYNC_ import SubmissionProcedures
from .comment._ASYNC_ import CommentProcedures
from .subreddit._ASYNC_ import SubredditProcedures
from .comment_tree._ASYNC_ import CommentTreeProcedures
from .front._ASYNC_ import FrontProcedures
from .user._ASYNC_ import UserProcedures
from .account._ASYNC_ import AccountProcedures
from .collection._ASYNC_ import CollectionProcedures
from .flair._ASYNC_ import FlairProcedures
from .flair_emoji._ASYNC_ import FlairEmojiProcedures
from .custom_feed._ASYNC_ import CustomFeedProcedures
from .live_thread._ASYNC_ import LiveThreadProcedures
from .message._ASYNC_ import MessageProcedures
from .moderation._ASYNC_ import ModerationProcedures
from .draft._ASYNC_ import DraftProcedures
from .misc._ASYNC_ import MiscProcedures
from .modmail._ASYNC_ import ModmailProcedures
from .widget._ASYNC_ import WidgetProcedures
from .wiki._ASYNC_ import WikiProcedures
from .legacy_reddit_subreddit_style._ASYNC_ import LegacyRedditSubredditStyleProcedures
from .redesign_reddit_subreddit_style._ASYNC_ import RedesignRedditSubredditStyleProcedures

class SiteProcedures:
    def __init__(self, client: Client):
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
        self.legacy_reddit_subreddit_style: LegacyRedditSubredditStyleProcedures = LegacyRedditSubredditStyleProcedures(client)
        self.redesign_reddit_subreddit_style: RedesignRedditSubredditStyleProcedures = RedesignRedditSubredditStyleProcedures(client)
