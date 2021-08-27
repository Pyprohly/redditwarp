
from __future__ import annotations
from typing import Mapping, Any, Sequence, Iterator, Union, overload

from datetime import datetime, timezone

class LiveThread:
    def __init__(self, d: Mapping[str, Any]):
        self.d = d
        self.idt: str = d['id']
        self.title: str = d['title']
        self.created_ut = int(d['created_utc'])
        self.created_at = datetime.fromtimestamp(self.created_ut, timezone.utc)
        self.description: str = d['description']
        self.description_html: str = d['description_html']
        self.resources: str = d['resources']
        self.resources_html: str = d['resources_html']
        self.websocket_url: str = d['websocket_url']
        self.is_closed: bool = d['state'] == 'complete'
        self.nsfw: bool = d['nsfw']
        self.viewer_count: int = d['viewer_count']

class LiveThreadUpdate:
    def __init__(self, d: Mapping[str, Any]):
        self.d = d
        self.uuid: str = d['id']
        self.author_name: str = d['author']
        self.body: str = d['body']
        self.body_html: str = d['body_html']
        self.created_ut = int(d['created_utc'])
        self.created_at = datetime.fromtimestamp(self.created_ut, timezone.utc)
        self.stricken: bool = d['stricken']


class Contributor:
    def __init__(self, d: Mapping[str, Any]):
        self.d = d
        self.name: str = d['name']
        full_id36: str = d['id']
        _, _, id36 = full_id36.partition('_')
        self.id36: str = id36
        self.id = int(id36, 36)
        self.permissions: Sequence[str] = d['permissions']

class ContributorList(Sequence[Contributor]):
    def __init__(self,
            contributors: Sequence[Contributor],
            invitations: Sequence[Contributor]):
        self.contributors = contributors
        self.invitations = invitations

    def __len__(self) -> int:
        return len(self.contributors)

    def __contains__(self, item: object) -> bool:
        return item in self.contributors

    def __iter__(self) -> Iterator[Contributor]:
        return iter(self.contributors)

    @overload
    def __getitem__(self, index: int) -> Contributor: ...
    @overload
    def __getitem__(self, index: slice) -> Sequence[Contributor]: ...
    def __getitem__(self, index: Union[int, slice]) -> Union[Contributor, Sequence[Contributor]]:
        return self.contributors[index]
