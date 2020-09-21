
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .submission_base import (
    SubmissionBase,
    TextPostBase,
    LinkPostBase,
)

class Submission(SubmissionBase):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client = client

class TextPost(Submission, TextPostBase):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d, client)

class LinkPost(Submission, LinkPostBase):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d, client)
