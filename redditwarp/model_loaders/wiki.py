
from __future__ import annotations
from typing import Mapping, Any

from ..models.wiki import (
    WikiPageRevisionAuthorUser,
    WikiPage,
    WikiPageRevision,
    WikiPageSettings,
)


def load_wiki_page_revision_author_user(d: Mapping[str, Any]) -> WikiPageRevisionAuthorUser:
    return WikiPageRevisionAuthorUser(d)


def load_wiki_page(d: Mapping[str, Any]) -> WikiPage:
    return WikiPage(
        d=d,
        body=d['content_md'],
        body_html=d['content_html'],
        can_revise=d['may_revise'],
        revision_uuid=d['revision_id'],
        revision_unixtime=d['revision_date'],
        revision_author=load_wiki_page_revision_author_user(d['revision_by']['data']),
        revision_message=d['reason'] or '',
    )

def load_wiki_page_revision(d: Mapping[str, Any]) -> WikiPageRevision:
    return WikiPageRevision(
        d=d,
        uuid=d['id'],
        unixtime=d['unixtime'],
        author=load_wiki_page_revision_author_user(d['author']['data']),
        message=d['reason'] or '',
        hidden=d['revision_hidden'],
    )


def load_wiki_page_settings(d: Mapping[str, Any]) -> WikiPageSettings:
    return WikiPageSettings(
        permlevel=d['permlevel'],
        editors=[load_wiki_page_revision_author_user(m['data']) for m in d['editors']],
        unlisted=not d['listed'],
    )
