
from __future__ import annotations
from typing import Mapping, Any

from ..models.wiki_base import BaseWikiPageRevisionAuthorUser, BaseWikiPage, BaseWikiPageRevision, BaseWikiPageSettings


def load_base_wiki_page_revision_author_user(d: Mapping[str, Any]) -> BaseWikiPageRevisionAuthorUser:
    return BaseWikiPageRevisionAuthorUser(d)


def load_base_wiki_page(d: Mapping[str, Any]) -> BaseWikiPage:
    return BaseWikiPage(
        d=d,
        body=d['content_md'],
        body_html=d['content_html'],
        can_revise=d['may_revise'],
        revision_uuid=d['revision_id'],
        revision_timestamp=d['revision_date'],
        revision_author=load_base_wiki_page_revision_author_user(d['revision_by']['data']),
        revision_message=d['reason'] or '',
    )

def load_base_wiki_page_revision(d: Mapping[str, Any]) -> BaseWikiPageRevision:
    return BaseWikiPageRevision(
        d=d,
        uuid=d['id'],
        timestamp=d['timestamp'],
        author=load_base_wiki_page_revision_author_user(d['author']['data']),
        message=d['reason'] or '',
        hidden=d['revision_hidden'],
    )


def load_base_wiki_page_settings(d: Mapping[str, Any]) -> BaseWikiPageSettings:
    return BaseWikiPageSettings(
        permlevel=d['permlevel'],
        # Type ignore due to https://github.com/python/mypy/issues/10986
        editors=[load_base_wiki_page_revision_author_user(m['data']) for m in d['editors']],  # type: ignore[misc]
        unlisted=not d['listed'],
    )
