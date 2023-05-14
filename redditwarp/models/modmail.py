
from __future__ import annotations
from typing import Any, Optional, Sequence, Mapping

from datetime import datetime
from dataclasses import dataclass
from enum import IntEnum

from .datamemento import DatamementoPropertiesMixin


class ConversationProgress(IntEnum):
    NEW = 0
    IN_PROGRESS = 1
    ARCHIVED = 2

class ModActionType(IntEnum):
    HIGHLIGHT = 0
    UNHIGHLIGHT = 1
    ARCHIVE = 2
    UNARCHIVE = 3
    MUTE_USER = 5
    UNMUTE_USER = 6
    BAN_USER = 7
    UNBAN_USER = 8
    APPROVE_USER = 9
    DISAPPROVE_USER = 10


@dataclass(repr=False, eq=False)
class ModmailSubreddit(DatamementoPropertiesMixin):
    d: Mapping[str, Any]
    id: int
    name: str
    subscriber_count: int


class ConversationInfo(DatamementoPropertiesMixin):
    @dataclass(repr=False, eq=False)
    class LegacyMessage:
        id: int
        idn: int
        id36: str
        link: str

    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        ("")
        self.id36: str = d['id']
        ("")
        self.idn: int = int(self.id36, 36)
        ("")
        self.id: int = self.idn
        ("")
        self.subject: str = d['subject']
        ("")
        self.progress: int = d['state']
        ("""
            Enum: :class:`.ConversationProgress`
            """)
        self.message_count: int = d['numMessages']
        ("""
            Number of messages in the conversation.
            """)
        self.auto: bool = d['isAuto']
        ("""
            True if the conversation was created due to an automated message;
            false if the message was created by a user.
            """)
        self.internal: bool = d['isInternal']
        ("""
            Whether this conversation is a moderator discussion.
            """)
        self.repliable: bool = d['isRepliable']
        ("""
            True if the conversation thread accepts replies.
            """)
        self.highlighted: bool = d['isHighlighted']
        ("""
            True if the conversation is highlighted.
            """)

        self.legacy_message: Optional[ConversationInfo.LegacyMessage] = None
        ("""
            Object that contains an ID that refers to the first message in the
            legacy modmail thread for this conversation thread.

            The underlying data can be null in rare cases, such as in the
            "r/{subreddit} is now enrolled in the New Modmail"
            modmail message from u/reddit.
            """)
        if (x := d['legacyFirstMessageId']) is not None:
            self.legacy_message = self.LegacyMessage(
                id36=x,
                idn=(idn := int(x, 36)),
                # https://github.com/python/mypy/issues
                id=idn,  # type: ignore[has-type]
                link="https://www.reddit.com/message/messages/" + x,
            )

        self.last_updated_by_user_at: Optional[datetime] = (x := d['lastUserUpdate']) and datetime.fromisoformat(x)
        ("""
            If :attr:`internal` is true this should always be null.
            """)
        self.last_updated_by_mod_at: Optional[datetime] = (x := d['lastModUpdate']) and datetime.fromisoformat(x)
        ("")
        self.last_updated_at: datetime = datetime.fromisoformat(d['lastUpdated'])
        ("""
            Same as either :attr:`last_updated_by_user_at` or :attr:`last_updated_by_mod_at`, whichever is newer.
            """)
        self.last_unread: Optional[datetime] = (x := d['lastUnread']) and datetime.fromisoformat(x)
        ("""
            Datetime of when the conversation was last marked unread.
            """)
        owner = d['owner']
        self.subreddit_name: str = owner['displayName']
        ("""
            Name of the subreddit associated with this conversation.
            """)
        self.subreddit_id: int = int(owner['id'][3:], 36)
        ("""
            ID of the subreddit associated with this conversation.
            """)

class Message(DatamementoPropertiesMixin):
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        ("")
        self.id36: str = d['id']
        ("")
        self.idn: int = int(self.id36, 36)
        ("")
        self.id: int = self.idn
        ("")
        author = d['author']
        self.author_name: str = author['name']
        ("""
            User name of the author of the message.

            Unknown what happens if the user is deleted.
            Is the value `[deleted]`, an empty string, or does the field in the
            underlying object not exist?
            If you have any information about this, please open an issue report at
            `<https://github.com/Pyprohly/redditwarp/issues>`_.
            """)
        self.author_id: int = author['id']
        ("""
            User ID of the author of the message.

            Unknown what happens if the user is deleted.
            If you have any information about this, please open an issue report at
            `<https://github.com/Pyprohly/redditwarp/issues>`_.
            """)
        self.body: str = d['bodyMarkdown']
        ("""
            Text content of the message in markdown format.
            """)
        self.body_html: str = d['body']
        ("""
            Content of the message in HTML.
            """)
        self.datetime: datetime = datetime.fromisoformat(d['date'])
        ("""
            Datetime object of when the message was created.
            """)
        self.internal: bool = d['isInternal']
        ("""
            Always true if this message is in a moderator discussion.
            Otherwise, true if this message is a private moderator note.
            """)

class ModAction(DatamementoPropertiesMixin):
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        ("")
        self.id: int = int(d['id'], 36)
        ("")
        self.action_type: int = d['actionTypeId']
        ("""
            Enum: :class:`.ModActionType`
            """)
        self.agent_name: str = d['author']['name']
        ("""
            Name of the mod who performed the action.

            Unknown what happens if the user is deleted.
            Is the value `[deleted]`, an empty string, or does the field in the
            underlying object not exist?
            If you have any information about this, please open an issue report at
            `<https://github.com/Pyprohly/redditwarp/issues>`_.
            """)
        self.agent_id: int = d['author']['id']
        ("""
            User ID of the mod who performed the action.

            Unknown what happens if the user is deleted.
            If you have any information about this, please open an issue report at
            `<https://github.com/Pyprohly/redditwarp/issues>`_.
            """)
        self.datetime: datetime = datetime.fromisoformat(d['date'])
        ("""
            Datetime object of when the action was performed.
            """)

class UserDossier(DatamementoPropertiesMixin):
    @dataclass(repr=False, eq=False)
    class RecentPost:
        id: int
        ("""
            The submission ID.
            """)
        permalink: str
        ("""
            A URL to the submission.
            """)
        title: str
        ("""
            Title of the submission.
            """)
        created_at: datetime
        ("""
            When the submission was created.
            """)

    @dataclass(repr=False, eq=False)
    class RecentComment:
        id: int
        ("""
            The comment ID.
            """)
        permalink: str
        ("""
            A URL to the comment.
            """)
        submission_title: str
        ("""
            The title of the submission in which the comment resides.
            """)
        body: str
        ("""
            The comment the user wrote.
            """)
        created_at: datetime
        ("""
            When the comment was created.
            """)

    @dataclass(repr=False, eq=False)
    class RecentConvo:
        id: int
        ("""
            The conversation ID.
            """)
        subject: str
        ("""
            The subject line of the conversation.
            """)
        permalink: str
        ("""
            A URL to the conversation.

            E.g., https://mod.reddit.com/mail/perma/tiebu.
            """)

    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        ("")
        self.id: int = int(d['id'][3:], 36)
        ("")
        self.username: str = d['name']
        ("""
            The name of the target user.
            """)
        self.created_at: datetime = datetime.fromisoformat(d['created'])
        ("""
            When the user account was created.
            """)
        self.suspended: bool = d['isSuspended']
        ("""
            True if account is suspended.
            """)
        self.shadow_banned: bool = d['isShadowBanned']
        ("""
            True if account is shadow banned.
            """)
        self.approved_user: bool = d['approveStatus']['isApproved']
        ("""
            True if the user is an approved contributor on the subreddit.
            """)

        mute_status = d['muteStatus']
        self.muted: bool = mute_status['isMuted']
        ("""
            True if the user is currently muted on the subreddit.
            """)
        self.mute_reason: str = mute_status['reason']
        ("""
            Mute reason.

            Empty string if not currently muted.
            """)
        self.mute_count: int = mute_status['muteCount']
        ("""
            Number of times the user has been muted in the subreddit.
            """)
        self.mute_end_datetime: datetime = datetime.min if (x := mute_status['endDate']) is None else datetime.fromisoformat(x)
        ("""
            Datetime object of when the mute ends.

            Value is `datetime.min` if :attr:`muted` is false.
            """)

        ban_status = d['banStatus']
        self.banned: bool = ban_status['isBanned']
        ("""
            True if the user is currently banned on the subreddit.
            """)
        self.ban_reason: str = ban_status['reason']
        ("""
            Ban reason.

            Empty string if not currently banned.
            """)
        self.ban_permanent: bool = ban_status['isPermanent']
        ("""
            True if the ban is permanent.

            Value false if user is not banned.
            """)
        self.ban_end_datetime: datetime = datetime.min if (x := ban_status['endDate']) is None else datetime.fromisoformat(x)
        ("""
            Datetime object of when the ban ends.

            Value is `datetime.min` if :attr:`banned` is false.
            """)

        self.recent_posts: Sequence[UserDossier.RecentPost] = [
            self.RecentPost(
                id=int(k.partition('_')[-1], 36),
                permalink=v['permalink'],
                title=v['title'],
                created_at=datetime.fromisoformat(v['date']),
            )
            for k, v in d['recentPosts'].items()
        ]
        ("""
            A bit of information about the user's recent submissions to the subreddit.
            """)
        self.recent_comments: Sequence[UserDossier.RecentComment] = [
            self.RecentComment(
                id=int(k.partition('_')[-1], 36),
                permalink=v['permalink'],
                submission_title=v['title'],
                body=v['comment'],
                created_at=datetime.fromisoformat(v['date']),
            )
            for k, v in d['recentComments'].items()
        ]
        ("""
            A bit information about the user's recent comments in the subreddit.
            """)
        self.recent_convos: Sequence[UserDossier.RecentConvo] = [
            self.RecentConvo(
                id=int(v['id'], 36),
                subject=v['subject'],
                permalink=v['permalink'],
            )
            for _k, v in d['recentConvos'].items()
        ]
        ("""
            Other modmail conversations this user is involved in.
            """)


@dataclass(repr=False, eq=False, frozen=True)
class ConversationAggregate:
    info: ConversationInfo
    ("""
        Information about the conversation.
        """)
    messages: Sequence[Message]
    ("""
        Conversation messages.
        """)
    mod_actions: Sequence[ModAction]
    ("""
        Conversation mod actions.
        """)
    history: Sequence[object]
    ("""
        Conversation entries.

        Objects are either :attr:`.Message` or :attr:`.ModAction` instances.
        """)

@dataclass(repr=False, eq=False, frozen=True)
class UserDossierConversationAggregate(ConversationAggregate):
    user_dossier: UserDossier
    ("""
        Information about the target user.
        """)

@dataclass(repr=False, eq=False, frozen=True)
class OptionalUserDossierConversationAggregate(ConversationAggregate):
    user_dossier: Optional[UserDossier]
    ("""
        Information about the target user.
        """)
