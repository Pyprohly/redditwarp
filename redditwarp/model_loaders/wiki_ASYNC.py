
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ..client_ASYNC import Client

from ..models.wiki_base import BaseWikiPageRevisionAuthorUser
from ..models.wiki_ASYNC import WikiPageRevisionAuthorUser, WikiPage, WikiPageRevision, WikiPageSettings
from .wiki_base import load_base_wiki_page, load_base_wiki_page_revision, load_base_wiki_page_settings


def promote_base_wiki_page_revision_author_user(base: BaseWikiPageRevisionAuthorUser, client: Client) -> WikiPageRevisionAuthorUser:
    return WikiPageRevisionAuthorUser(base.d, client)


def load_wiki_page_revision_author_user(d: Mapping[str, Any], client: Client) -> WikiPageRevisionAuthorUser:
    return WikiPageRevisionAuthorUser(d, client)


def load_wiki_page(d: Mapping[str, Any], client: Client) -> WikiPage:
    up = load_base_wiki_page(d)
    return WikiPage(
        d=up.d,
        body=up.body,
        body_html=up.body_html,
        can_revise=up.can_revise,
        revision_uuid=up.revision_uuid,
        revision_unixtime=up.revision_unixtime,
        revision_author=promote_base_wiki_page_revision_author_user(up.revision_author, client),
        revision_message=up.revision_message,
    )

def load_wiki_page_revision(d: Mapping[str, Any], client: Client) -> WikiPageRevision:
    up = load_base_wiki_page_revision(d)
    return WikiPageRevision(
        d=up.d,
        uuid=up.uuid,
        unixtime=up.unixtime,
        author=promote_base_wiki_page_revision_author_user(up.author, client),
        message=up.message,
        hidden=up.hidden,
    )


def load_wiki_page_settings(d: Mapping[str, Any], client: Client) -> WikiPageSettings:
    up = load_base_wiki_page_settings(d)
    return WikiPageSettings(
        permlevel=up.permlevel,
        # Type ignore due to https://github.com/python/mypy/issues/10986
        editors=[promote_base_wiki_page_revision_author_user(o, client) for o in up.editors],  # type: ignore[misc]
        unlisted=up.unlisted,
    )
