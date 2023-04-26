
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.modmail_SYNC import ConversationInfo, Message
    from ..impls.stream_SYNC import IStandardStreamEventSubject
    from ...pagination.paginator import CursorPaginator

from ..impls.modmail_stream_SYNC import ModmailStream


def make_stream(paginator: CursorPaginator[tuple[ConversationInfo, Message]], past: Optional[Iterable[tuple[ConversationInfo, Message]]] = None) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    return ModmailStream(paginator, past=past)


def get_all_stream_paginator(client: Client) -> CursorPaginator[tuple[ConversationInfo, Message]]:
    return client.p.modmail.pull.all().get_paginator()
def create_all_stream(client: Client) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    return make_stream(get_all_stream_paginator(client))

def get_inbox_stream_paginator(client: Client) -> CursorPaginator[tuple[ConversationInfo, Message]]:
    return client.p.modmail.pull.inbox().get_paginator()
def create_inbox_stream(client: Client) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    return make_stream(get_inbox_stream_paginator(client))

def get_new_stream_paginator(client: Client) -> CursorPaginator[tuple[ConversationInfo, Message]]:
    return client.p.modmail.pull.new().get_paginator()
def create_new_stream(client: Client) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    return make_stream(get_new_stream_paginator(client))

def get_in_progress_stream_paginator(client: Client) -> CursorPaginator[tuple[ConversationInfo, Message]]:
    return client.p.modmail.pull.in_progress().get_paginator()
def create_in_progress_stream(client: Client) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    return make_stream(get_in_progress_stream_paginator(client))

def get_archived_stream_paginator(client: Client) -> CursorPaginator[tuple[ConversationInfo, Message]]:
    return client.p.modmail.pull.archived().get_paginator()
def create_archived_stream(client: Client) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    return make_stream(get_archived_stream_paginator(client))

def get_filtered_stream_paginator(client: Client) -> CursorPaginator[tuple[ConversationInfo, Message]]:
    return client.p.modmail.pull.filtered().get_paginator()
def create_filtered_stream(client: Client) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    return make_stream(get_filtered_stream_paginator(client))

def get_appeals_stream_paginator(client: Client) -> CursorPaginator[tuple[ConversationInfo, Message]]:
    return client.p.modmail.pull.appeals().get_paginator()
def create_appeals_stream(client: Client) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    return make_stream(get_appeals_stream_paginator(client))

def get_join_requests_stream_paginator(client: Client) -> CursorPaginator[tuple[ConversationInfo, Message]]:
    return client.p.modmail.pull.join_requests().get_paginator()
def create_join_requests_stream(client: Client) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    return make_stream(get_join_requests_stream_paginator(client))


def get_highlighted_stream_paginator(client: Client) -> CursorPaginator[tuple[ConversationInfo, Message]]:
    return client.p.modmail.pull.highlighted().get_paginator()
def create_highlighted_stream(client: Client) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    return make_stream(get_highlighted_stream_paginator(client))

def get_mod_stream_paginator(client: Client) -> CursorPaginator[tuple[ConversationInfo, Message]]:
    return client.p.modmail.pull.mod().get_paginator()
def create_mod_stream(client: Client) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    return make_stream(get_mod_stream_paginator(client))

def get_notifications_stream_paginator(client: Client) -> CursorPaginator[tuple[ConversationInfo, Message]]:
    return client.p.modmail.pull.notifications().get_paginator()
def create_notifications_stream(client: Client) -> IStandardStreamEventSubject[tuple[ConversationInfo, Message]]:
    return make_stream(get_notifications_stream_paginator(client))
