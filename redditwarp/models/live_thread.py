
from __future__ import annotations
from typing import Mapping, Any, Sequence, Iterator, Union, overload, Optional

from datetime import datetime, timezone

class LiveThread:
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        ("")
        self.idt: str = d['id']
        ("""
            E.g., `177beztuzebxj`.
            """)
        self.title: str = d['title']
        ("")
        self.created_ut: int = int(d['created_utc'])
        ("")
        self.created_at: datetime = datetime.fromtimestamp(self.created_ut, timezone.utc)
        ("")
        self.description: str = d['description']
        ("""
            Live thread description as markdown text.

            This is the text below the title.
            """)
        self.description_html: str = d['description_html']
        ("""
            Live thread description as HTML.
            """)
        self.resources: str = d['resources']
        ("""
            Sidebar text in markdown.
            """)
        self.resources_html: str = d['resources_html']
        ("""
            Sidebar text in HTML.
            """)
        self.websocket_url: str = d['websocket_url']
        ("""
            Websocket URL. Connect to this websocket to stream live updates.
            """)
        self.complete: bool = d['state'] == 'complete'
        ("""
            True if the live thread is marked complete.
            """)
        self.nsfw: bool = d['nsfw']
        ("")
        self.viewer_count: int = d['viewer_count']
        ("""
            Number of subscribers. Value is fuzzed
            """)

class LiveUpdate:
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        ("")
        self.uuid: str = d['id']
        ("""
            E.g., `890e9242-d7fb-11eb-b450-0ed185f1b209`.
            """)
        self.author: Optional[str] = d['author']
        ("""
            Name of the user who posted the update.

            Value null if the user account was deleted.
            """)
        self.body: str = d['body']
        ("""
            Markdown content body.
            """)
        self.body_html: str = d['body_html']
        ("""
            Content body in HTML.
            """)
        self.created_ut: int = int(d['created_utc'])
        ("")
        self.created_at: datetime = datetime.fromtimestamp(self.created_ut, timezone.utc)
        ("")
        self.stricken: bool = d['stricken']
        ("""
            True if the update has been stricken.
            """)

class Contributor:
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        ("")
        self.name: str = d['name']
        ("""
            Name of a user; name of the contributor.
            """)
        full_id36: str = d['id']
        _, _, id36 = full_id36.partition('_')
        self.id36: str = id36
        ("""
            Contributor's user ID as a base 36 number.
            """)
        self.id: int = int(id36, 36)
        ("""
            Contributor's user ID.
            """)
        self.permissions: Sequence[str] = d['permissions']
        ("""
            Values: `all`, `close`, `discussions`, `edit`, `manage`, `settings`, `update`.

            Can be empty. This means no permissions.
            """)

class ContributorList(Sequence[Contributor]):
    def __init__(self,
            contributors: Sequence[Contributor],
            invitations: Sequence[Contributor]) -> None:
        self.contributors: Sequence[Contributor] = contributors
        ("")
        self.invitations: Sequence[Contributor] = invitations
        ("")

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
