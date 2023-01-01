
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .submission.SYNC import SubmissionProcedures
from .comment.SYNC import CommentProcedures
from .subreddit.SYNC import SubredditProcedures
from .comment_tree.SYNC import CommentTreeProcedures
from .front.SYNC import FrontProcedures
from .user.SYNC import UserProcedures
from .account.SYNC import AccountProcedures
from .collection.SYNC import CollectionProcedures
from .flair.SYNC import FlairProcedures
from .flair_emoji.SYNC import FlairEmojiProcedures
from .custom_feed.SYNC import CustomFeedProcedures
from .live_thread.SYNC import LiveThreadProcedures
from .message.SYNC import MessageProcedures
from .moderation.SYNC import ModerationProcedures
from .draft.SYNC import DraftProcedures
from .misc.SYNC import MiscProcedures
from .modmail.SYNC import ModmailProcedures
from .widget.SYNC import WidgetProcedures
from .wiki.SYNC import WikiProcedures
from .legacy_reddit_subreddit_style.SYNC import LegacyRedditSubredditStyleProcedures
from .redesign_reddit_subreddit_style.SYNC import RedesignRedditSubredditStyleProcedures

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
        self.legacy_reddit_subreddit_style: LegacyRedditSubredditStyleProcedures = LegacyRedditSubredditStyleProcedures(client)
        self.redesign_reddit_subreddit_style: RedesignRedditSubredditStyleProcedures = RedesignRedditSubredditStyleProcedures(client)
