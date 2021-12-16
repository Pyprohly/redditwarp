
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .submission._SYNC_ import Submission
from .comment._SYNC_ import Comment
from .subreddit._SYNC_ import Subreddit
from .comment_tree._SYNC_ import CommentTree
from .front._SYNC_ import Front
from .user._SYNC_ import User
from .account._SYNC_ import Account
from .collection._SYNC_ import Collection
from .flair._SYNC_ import Flair
from .flair_emoji._SYNC_ import FlairEmoji
from .custom_feed._SYNC_ import CustomFeed
from .live_thread._SYNC_ import LiveThread
from .message._SYNC_ import Message
from .moderation._SYNC_ import Moderation
from .draft._SYNC_ import Draft
from .misc._SYNC_ import Misc
from .modmail._SYNC_ import Modmail
from .widget._SYNC_ import Widget
from .wiki._SYNC_ import Wiki
from .legacy_reddit_subreddit_style._SYNC_ import LegacyRedditSubredditStyle
from .redesign_reddit_subreddit_style._SYNC_ import RedesignRedditSubredditStyle

class SiteProcedures:
    def __init__(self, client: Client):
        self._client = client
        self.submission: Submission = Submission(client)
        self.comment: Comment = Comment(client)
        self.subreddit: Subreddit = Subreddit(client)
        self.comment_tree: CommentTree = CommentTree(client)
        self.front: Front = Front(client)
        self.user: User = User(client)
        self.account: Account = Account(client)
        self.collection: Collection = Collection(client)
        self.flair: Flair = Flair(client)
        self.flair_emoji: FlairEmoji = FlairEmoji(client)
        self.custom_feed: CustomFeed = CustomFeed(client)
        self.live_thread: LiveThread = LiveThread(client)
        self.message: Message = Message(client)
        self.moderation: Moderation = Moderation(client)
        self.draft: Draft = Draft(client)
        self.misc: Misc = Misc(client)
        self.modmail: Modmail = Modmail(client)
        self.widget: Widget = Widget(client)
        self.wiki: Wiki = Wiki(client)
        self.legacy_reddit_subreddit_style: LegacyRedditSubredditStyle = LegacyRedditSubredditStyle(client)
        self.redesign_reddit_subreddit_style: RedesignRedditSubredditStyle = RedesignRedditSubredditStyle(client)
