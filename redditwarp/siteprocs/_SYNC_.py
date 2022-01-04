
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .submission._SYNC_ import SubmissionProcedures
from .comment._SYNC_ import CommentProcedures
from .subreddit._SYNC_ import SubredditProcedures
from .comment_tree._SYNC_ import CommentTreeProcedures
from .front._SYNC_ import FrontProcedures
from .user._SYNC_ import UserProcedures
from .account._SYNC_ import AccountProcedures
from .collection._SYNC_ import CollectionProcedures
from .flair._SYNC_ import FlairProcedures
from .flair_emoji._SYNC_ import FlairEmojiProcedures
from .custom_feed._SYNC_ import CustomFeedProcedures
from .live_thread._SYNC_ import LiveThreadProcedures
from .message._SYNC_ import MessageProcedures
from .moderation._SYNC_ import ModerationProcedures
from .draft._SYNC_ import DraftProcedures
from .misc._SYNC_ import MiscProcedures
from .modmail._SYNC_ import ModmailProcedures
from .widget._SYNC_ import WidgetProcedures
from .wiki._SYNC_ import WikiProcedures
from .legacy_reddit_subreddit_style._SYNC_ import LegacyRedditSubredditStyleProcedures
from .redesign_reddit_subreddit_style._SYNC_ import RedesignRedditSubredditStyleProcedures

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
