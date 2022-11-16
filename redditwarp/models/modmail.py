
from __future__ import annotations
from typing import Any, Optional, Sequence, Generic, Mapping, TypeVar

from datetime import datetime
from dataclasses import dataclass
from enum import IntEnum

from .artifact import IArtifact


class ConversationProgress(IntEnum):
    NEW = 0
    IN_PROGRESS = 1
    ARCHIVED = 2

class ModmailModActionType(IntEnum):
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
class ModmailModeratedSubreddit(IArtifact):
    d: Mapping[str, Any]
    id: int
    name: str
    subscriber_count: int


class Conversation(IArtifact):
    @dataclass(repr=False, eq=False)
    class LegacyMessage:
        id: int
        id36: str
        link: str

    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        self.id36: str = d['id']
        self.id: int = int(self.id36, 36)
        self.subject: str = d['subject']
        self.progress: int = d['state']
        self.message_count: int = d['numMessages']
        self.is_auto: bool = d['isAuto']
        self.is_internal: bool = d['isInternal']
        self.is_repliable: bool = d['isRepliable']
        self.is_highlighted: bool = d['isHighlighted']

        self.legacy_message: Optional[Conversation.LegacyMessage] = None
        if (x := d['legacyFirstMessageId']) is not None:
            self.legacy_message = self.LegacyMessage(
                id36=x,
                id=int(x, 36),
                link="https://www.reddit.com/message/messages/" + x,
            )

        self.last_user_update: Optional[datetime] = None if (x := d['lastUserUpdate']) is None else datetime.fromisoformat(x)
        self.last_mod_update: Optional[datetime] = None if (x := d['lastModUpdate']) is None else datetime.fromisoformat(x)
        self.last_update: datetime = datetime.fromisoformat(d['lastUpdated'])
        self.last_unread: Optional[datetime] = None if (x := d['lastUnread']) is None else datetime.fromisoformat(x)
        owner = d['owner']
        self.subreddit_name: str = owner['displayName']
        self.subreddit_id: int = int(owner['id'][3:], 36)

class Message(IArtifact):
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        self.id36: str = d['id']
        self.id: int = int(self.id36, 36)
        author = d['author']
        self.author_name: str = author['name']
        self.author_id: int = author['id']
        self.body_text: str = d['bodyMarkdown']
        self.body_html: str = d['body']
        self.datetime: datetime = datetime.fromisoformat(d['date'])
        self.is_internal: bool = d['isInternal']

class ModmailModAction(IArtifact):
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        self.id: int = int(d['id'], 36)
        self.action_type: int = d['actionTypeId']
        self.agent_name: str = d['author']['name']
        self.agent_id: int = d['author']['id']
        self.datetime: datetime = datetime.fromisoformat(d['date'])

class UserDossier(IArtifact):
    class RecentPost:
        def __init__(self, d: Mapping[str, Any]) -> None:
            self.permalink: str
            self.title: str
            self.created_at: datetime

    class RecentComment:
        def __init__(self, d: Mapping[str, Any]) -> None:
            self.permalink: str
            self.title: str
            self.body: str
            self.created_at: datetime

    class RecentConvo:
        def __init__(self, d: Mapping[str, Any]) -> None:
            self.id: int
            self.subject: str
            self.permalink: str

    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        self.id: int = int(d['id'][3:], 36)
        self.name: str = d['name']
        self.created_at: datetime = datetime.fromisoformat(d['created'])
        self.is_shadow_banned: bool = d['isShadowBanned']
        self.is_approved: bool = d['approveStatus']['isApproved']
        mute_status = d['muteStatus']
        self.is_muted: bool = mute_status['isMuted']
        self.mute_reason: str = mute_status['reason']
        self.mute_count: int = mute_status['muteCount']
        self.mute_end_datetime: datetime = datetime.min if (x := mute_status['endDate']) is None else datetime.fromisoformat(x)
        ban_status = d['banStatus']
        self.is_banned: bool = ban_status['isBanned']
        self.ban_reason: str = ban_status['reason']
        self.ban_is_permanent: bool = ban_status['isPermanent']
        self.ban_end_datetime: datetime = datetime.min if (x := ban_status['endDate']) is None else datetime.fromisoformat(x)
        self.recent_posts: Sequence[UserDossier.RecentPost] = [self.RecentPost(m) for m in d['recentPosts']]
        self.recent_comments: Sequence[UserDossier.RecentComment] = [self.RecentComment(m) for m in d['recentComments']]
        self.recent_convos: Sequence[UserDossier.RecentConvo] = [self.RecentConvo(m) for m in d['recentConvos']]


TConversation = TypeVar('TConversation', bound=Conversation)
TMessage = TypeVar('TMessage', bound=Message)
TModmailModAction = TypeVar('TModmailModAction', bound=ModmailModAction)

class GBaseConversationAggregate(Generic[TConversation, TMessage, TModmailModAction]):
    def __init__(self,
            conversation: TConversation,
            messages: Sequence[TMessage],
            mod_actions: Sequence[TModmailModAction],
            history: Sequence[object]) -> None:
        self.conversation: TConversation = conversation
        self.messages: Sequence[TMessage] = messages
        self.mod_actions: Sequence[TModmailModAction] = mod_actions
        self.history: Sequence[object] = history

class ConversationAggregate(GBaseConversationAggregate[Conversation, Message, ModmailModAction]):
    pass

TUserDossier = TypeVar('TUserDossier', bound=UserDossier)

class GBaseUserDossierConversationAggregate(
    GBaseConversationAggregate[TConversation, TMessage, TModmailModAction],
    Generic[TConversation, TMessage, TModmailModAction, TUserDossier],
):
    def __init__(self,
            conversation: TConversation,
            messages: Sequence[TMessage],
            mod_actions: Sequence[TModmailModAction],
            history: Sequence[object],
            user_dossier: TUserDossier) -> None:
        super().__init__(conversation, messages, mod_actions, history)
        self.user_dossier: TUserDossier = user_dossier

class UserDossierConversationAggregate(GBaseUserDossierConversationAggregate[Conversation, Message, ModmailModAction, UserDossier]):
    pass

class GBaseOptionalUserDossierConversationAggregate(
    GBaseConversationAggregate[TConversation, TMessage, TModmailModAction],
    Generic[TConversation, TMessage, TModmailModAction, TUserDossier],
):
    def __init__(self,
            conversation: TConversation,
            messages: Sequence[TMessage],
            mod_actions: Sequence[TModmailModAction],
            history: Sequence[object],
            user_dossier: Optional[TUserDossier]) -> None:
        super().__init__(conversation, messages, mod_actions, history)
        self.user_dossier: Optional[TUserDossier] = user_dossier

class OptionalUserDossierConversationAggregate(GBaseOptionalUserDossierConversationAggregate[Conversation, Message, ModmailModAction, UserDossier]):
    pass
