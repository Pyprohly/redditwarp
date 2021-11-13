
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ..client_SYNC import Client

from dataclasses import dataclass

from .wiki_base import (
    BaseWikiPageRevisionAuthorUser,
    GenericBaseWikiPage,
    GenericBaseWikiPageRevision,
    GenericBaseWikiPageSettings,
)

class WikiPageRevisionAuthorUser(BaseWikiPageRevisionAuthorUser):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client: Client = client

@dataclass(repr=False, eq=False)
class WikiPage(GenericBaseWikiPage[WikiPageRevisionAuthorUser]):
    pass

@dataclass(repr=False, eq=False)
class WikiPageRevision(GenericBaseWikiPageRevision[WikiPageRevisionAuthorUser]):
    pass

@dataclass(repr=False, eq=False)
class WikiPageSettings(GenericBaseWikiPageSettings[WikiPageRevisionAuthorUser]):
    pass
