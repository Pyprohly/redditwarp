
from __future__ import annotations
from typing import Mapping, Any, Sequence, TypeVar, overload, Iterator, Union, final, Callable

from datetime import datetime, timezone

from .artifact import IArtifact
from ..model_loaders.submission import load_submission
from .submission import Submission

class SubmissionCollectionInfo(IArtifact):
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        self.uuid: str = d['collection_id']

        full_id36: str = d['subreddit_id']
        _, _, id36 = full_id36.partition('_')
        self.subreddit_id36: str = id36
        self.subreddit_id: int = int(id36, 36)

        full_id36 = d['author_id']
        _, _, id36 = full_id36.partition('_')
        self.author_id36: str = id36
        self.author_id: int = int(id36, 36)

        self.author_name: str = d['author_name']
        self.title: str = d['title']
        self.description: str = d['description']

        self.created_ts: float = d['created_at_utc']
        self.created_at: datetime = datetime.fromtimestamp(self.created_ts, timezone.utc)
        self.last_post_added_ut: float = d['last_update_utc']
        self.last_post_added_at: datetime = datetime.fromtimestamp(self.last_post_added_ut, timezone.utc)

        self.display_layout: str = d['display_layout'] or ''
        ("""
            Either: empty string, `TIMELINE`, or `GALLERY`.

            Value is an empty string on new collections. Empty string is treated the same as `TIMELINE`.
            """)
        self.layout: str = 'TIMELINE'
        ("""
            Either `TIMELINE` or `GALLERY`.

            This is the same as the :attr:`display_layout` attribute but the empty string is changed to `TIMELINE`.
            """)
        if self.display_layout:
            self.layout = self.display_layout

        submission_full_id36s: Sequence[str] = d['link_ids']
        self.submission_id36s: Sequence[str] = [s[3:] for s in submission_full_id36s]
        ("""
            List of submission ID36s contained in the collection.
            """)
        self.submission_ids: Sequence[int] = [int(s, 36) for s in self.submission_id36s]
        ("""
            List of submission IDs contained in the collection.
            """)

class SubmissionCollection(SubmissionCollectionInfo, Sequence[Submission]):
    @property
    def submissions(self) -> Sequence[Submission]:
        """List of submission objects contained in the collection."""
        return self.__submissions

    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.__submissions: Sequence[Submission] = ()
        # https://github.com/python/mypy/issues/4177
        if self.__class__.submissions == __class__.submissions:  # type: ignore[name-defined]
            self.__submissions = self._load_submissions(d, load_submission)

    def __len__(self) -> int:
        return len(self.__submissions)

    def __contains__(self, item: object) -> bool:
        return item in self.__submissions

    def __iter__(self) -> Iterator[Submission]:
        return iter(self.__submissions)

    @overload
    def __getitem__(self, index: int) -> Submission: ...
    @overload
    def __getitem__(self, index: slice) -> Sequence[Submission]: ...
    def __getitem__(self, index: Union[int, slice]) -> Union[Submission, Sequence[Submission]]:
        return self.__submissions[index]

    _TSubmission = TypeVar('_TSubmission', bound=Submission)

    @final
    def _load_submissions(self,
        d: Mapping[str, Any],
        load: Callable[[Mapping[str, Any]], _TSubmission],
    ) -> Sequence[_TSubmission]:
        children_data = d['sorted_links']['data']['children']
        return [load(i['data']) for i in children_data]
