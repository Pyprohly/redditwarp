
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....client_SYNC import Client
    from .....models.moderation_action_log_entry import ModerationActionLogEntry
    from ..stream import IStandardStreamEventSubject

from ..stream import Stream


def make_action_log_stream(client: Client, sr: str) -> IStandardStreamEventSubject[ModerationActionLogEntry]:
    it = client.p.moderation.pull_actions(sr)
    paginator = it.get_paginator()
    return Stream(paginator, lambda x: x.uuid)
