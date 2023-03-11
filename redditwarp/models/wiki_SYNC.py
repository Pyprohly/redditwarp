
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping, Sequence
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .wiki import (
    WikiPageRevisionAuthorUser as BaseWikiPageRevisionAuthorUser,
    WikiPage as BaseWikiPage,
    WikiPageRevision as BaseWikiPageRevision,
    WikiPageSettings as BaseWikiPageSettings,
)

class WikiPageRevisionAuthorUser(BaseWikiPageRevisionAuthorUser):
    def __init__(self, d: Mapping[str, Any], client: Client) -> None:
        super().__init__(d)
        self.client: Client = client
        ("")


class WikiPage(BaseWikiPage):
    revision_author: WikiPageRevisionAuthorUser

class WikiPageRevision(BaseWikiPageRevision):
    author: WikiPageRevisionAuthorUser

class WikiPageSettings(BaseWikiPageSettings):
    editors: Sequence[WikiPageRevisionAuthorUser]
