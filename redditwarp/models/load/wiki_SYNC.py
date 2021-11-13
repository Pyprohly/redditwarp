
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ..wiki_base import BaseWikiPageRevisionAuthorUser
from ..wiki_SYNC import WikiPageRevisionAuthorUser, WikiPage, WikiPageRevision, WikiPageSettings
from .wiki_base import load_base_wiki_page, load_base_wiki_page_revision, load_base_wiki_page_settings


def promote_wiki_page_revision_author_user_from_base(base: BaseWikiPageRevisionAuthorUser, client: Client) -> WikiPageRevisionAuthorUser:
    return WikiPageRevisionAuthorUser(base.d, client)

def load_wiki_page_revision_author_user(d: Mapping[str, Any], client: Client) -> WikiPageRevisionAuthorUser:
    return WikiPageRevisionAuthorUser(d, client)


def load_wiki_page(d: Mapping[str, Any], client: Client) -> WikiPage:
    u = load_base_wiki_page(d)
    return WikiPage(
        d=u.d,
        body=u.body,
        body_html=u.body_html,
        can_revise=u.can_revise,
        revision_uuid=u.revision_uuid,
        revision_timestamp=u.revision_timestamp,
        revision_author=promote_wiki_page_revision_author_user_from_base(u.revision_author, client),
        revision_message=u.revision_message,
    )

def load_wiki_page_revision(d: Mapping[str, Any], client: Client) -> WikiPageRevision:
    u = load_base_wiki_page_revision(d)
    return WikiPageRevision(
        d=u.d,
        uuid=u.uuid,
        timestamp=u.timestamp,
        author=promote_wiki_page_revision_author_user_from_base(u.author, client),
        message=u.message,
        hidden=u.hidden,
    )


def load_wiki_page_settings(d: Mapping[str, Any], client: Client) -> WikiPageSettings:
    u = load_base_wiki_page_settings(d)
    return WikiPageSettings(
        permlevel=u.permlevel,
        # Type ignore due to https://github.com/python/mypy/issues/10986
        editors=[promote_wiki_page_revision_author_user_from_base(o, client) for o in u.editors],  # type: ignore[misc]
        unlisted=u.unlisted,
    )
