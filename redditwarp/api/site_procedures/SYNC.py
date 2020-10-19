
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...client_SYNC import Client

from .submission.SYNC import Submission
from .comment.SYNC import Comment
from .subreddit.SYNC import Subreddit
from .thread.SYNC import Thread
from .frontpage.SYNC import FrontPage
from .user.SYNC import User
from .account.SYNC import Account

class SiteProcedures:
    def __init__(self, client: Client):
        self._client = client
        self.submission = Submission(client)
        self.comment = Comment(client)
        self.subreddit = Subreddit(client)
        self.thread = Thread(client)
        self.frontpage = FrontPage(client)
        self.user = User(client)
        self.account = Account(client)
