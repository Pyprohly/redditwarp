
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

class ClientProcedures:
    def __init__(self, client: Client):
        self._client = client
        self.submission = Submission(client)
        self.comment = Comment(client)
        self.subreddit = Subreddit(client)
        self.comment_tree = CommentTree(client)
        self.front = Front(client)
        self.user = User(client)
        self.account = Account(client)
        self.collection = Collection(client)
        self.flair = Flair(client)
        self.flair_emoji = FlairEmoji(client)
        self.custom_feed = CustomFeed(client)
        self.live_thread = LiveThread(client)
        self.message = Message(client)
        self.moderation = Moderation(client)
        self.draft = Draft(client)
        self.misc = Misc(client)
        self.modmail = Modmail(client)
