
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .submission.SYNC import Submission
from .comment.SYNC import Comment
from .subreddit.SYNC import Subreddit
from .comment_tree.SYNC import CommentTree
from .front.SYNC import Front
from .user.SYNC import User
from .account.SYNC import Account
from .collection.SYNC import Collection
from .flair.SYNC import Flair
from .flair_emoji.SYNC import FlairEmoji
from .custom_feed.SYNC import CustomFeed
from .live_thread.SYNC import LiveThread
from .message.SYNC import Message
from .moderation.SYNC import Moderation
from .draft.SYNC import Draft
from .misc.SYNC import Misc
from .modmail.SYNC import Modmail
from .widget.SYNC import Widget
from .wiki.SYNC import Wiki
from .legacy_reddit_subreddit_style.SYNC import LegacyRedditSubredditStyle
from .redesign_reddit_subreddit_style.SYNC import RedesignRedditSubredditStyle

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
