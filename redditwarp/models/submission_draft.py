
from __future__ import annotations
from typing import Sequence, overload, Iterator, Union, Mapping, Any, Optional

from datetime import datetime
from dataclasses import dataclass

from .datamemento import DatamementoDataclassesMixin
from .subreddit import Subreddit

@dataclass(repr=False, eq=False)
class SubmissionDraft(DatamementoDataclassesMixin):
    """
    A public draft link is of the following format:

    `https://www.reddit.com/user/{USERNAME}/draft/{self.uuid}`
    """
    @dataclass(repr=False, eq=False)
    class Flair:
        uuid: str
        ("""
            The chosen flair template UUID.
            """)
        text_mode: str
        ("""
            Either `text` or `richtext`.
            """)
        text: str
        ("""
            Flair text.
            """)
        bg_color: str
        ("""
            Reminder: cannot be an empty string since this is isn't a user flair.
            """)
        fg_color_scheme: str
        ("""
            Either `dark` or `light`.
            """)

    d: Mapping[str, Any]
    uuid: str
    created_at: datetime
    ("""
        Datetime object of when the draft was created.
        """)
    modified_at: datetime
    ("""
        Datetime object of when the draft was last modified.
        """)
    public: bool
    ("""
        Whether the draft's link is public.

        Only those with the link can find the draft.
        """)
    subreddit_id: Optional[int]
    ("""
        The ID36 of the target subreddit.

        Value is null if not chosen yet.
        """)
    title: str
    reply_notifications: bool
    spoiler: bool
    nsfw: bool
    oc: bool
    ("""
        Whether the post should be marked as 'original content'.
        """)
    flair: Optional[Flair]
    ("""
        A flair option from the target subreddit.

        Value `None` if no flair selected.
        """)


class TextPostDraft(SubmissionDraft):
    pass

@dataclass(repr=False, eq=False)
class MarkdownTextPostDraft(TextPostDraft):
    body: str
    ("""
        The body text of the submission draft. In markdown format.
        """)

class RichTextTextPostDraft(TextPostDraft):
    pass


@dataclass(repr=False, eq=False)
class LinkPostDraft(SubmissionDraft):
    link: str
    ("""
        The linked URL.
        """)



class SubmissionDraftList(Sequence[SubmissionDraft]):
    @property
    def subreddits(self) -> Sequence[Subreddit]:
        return self.__subreddits

    def __init__(self,
        drafts: Sequence[SubmissionDraft],
        subreddits: Sequence[Subreddit],
    ) -> None:
        self.drafts: Sequence[SubmissionDraft] = drafts
        ("")
        self.__subreddits: Sequence[Subreddit] = subreddits

    def __len__(self) -> int:
        return len(self.drafts)

    def __contains__(self, item: object) -> bool:
        return item in self.drafts

    def __iter__(self) -> Iterator[SubmissionDraft]:
        return iter(self.drafts)

    @overload
    def __getitem__(self, index: int) -> SubmissionDraft: ...
    @overload
    def __getitem__(self, index: slice) -> Sequence[SubmissionDraft]: ...
    def __getitem__(self, index: Union[int, slice]) -> Union[SubmissionDraft, Sequence[SubmissionDraft]]:
        return self.drafts[index]
