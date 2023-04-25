
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any, Optional
if TYPE_CHECKING:
    from ..client_ASYNC import Client
    from .comment_ASYNC import Comment

from .submission import (
    Submission as BaseSubmission,
    LinkPost as BaseLinkPost,
    TextPost as BaseTextPost,
    GalleryPost as BaseGalleryPost,
    PollPost as BasePollPost,
    CrosspostSubmission as BaseCrosspostSubmission,
)

class Submission(BaseSubmission):
    def __init__(self, d: Mapping[str, Any], client: Client) -> None:
        super().__init__(d)
        self.client: Client = client
        ("")

    async def reply(self, text: str) -> Comment:
        return await self.client.p.submission.reply(self.id, text)

    async def delete(self) -> None:
        await self.client.p.submission.delete(self.id)

    async def lock(self) -> None:
        await self.client.p.submission.lock(self.id)

    async def unlock(self) -> None:
        await self.client.p.submission.unlock(self.id)

    async def distinguish(self) -> Submission:
        return await self.client.p.submission.distinguish(self.id)

    async def undistinguish(self) -> Submission:
        return await self.client.p.submission.undistinguish(self.id)

    async def sticky(self, slot: Optional[int] = None) -> None:
        await self.client.p.submission.sticky(self.id, slot)

    async def unsticky(self) -> None:
        await self.client.p.submission.unsticky(self.id)

    async def approve(self) -> None:
        await self.client.p.submission.approve(self.id)

    async def remove(self) -> None:
        await self.client.p.submission.remove(self.id)

    async def apply_removal_reason(self,
            reason_id: Optional[str],
            note: Optional[str] = None) -> None:
        await self.client.p.submission.apply_removal_reason(self.id, reason_id, note)

    async def send_removal_comment(self,
            title: str,
            message: str) -> Comment:
        return await self.client.p.submission.send_removal_comment(self.id, title, message)

    async def send_removal_message(self,
            title: str,
            message: str,
            *,
            exposed: bool = False) -> None:
        await self.client.p.submission.send_removal_message(self.id, title, message, exposed=exposed)


class LinkPost(Submission, BaseLinkPost):
    pass

class TextPost(Submission, BaseTextPost):
    async def edit_body(self, text: str) -> TextPost:
        return await self.client.p.submission.edit_text_post_body(self.id, text)

class GalleryPost(Submission, BaseGalleryPost):
    pass

class PollPost(Submission, BasePollPost):
    pass

class CrosspostSubmission(Submission, BaseCrosspostSubmission):
    @property
    def original(self) -> Optional[Submission]:
        return self.__original

    def __init__(self, d: Mapping[str, Any], client: Client) -> None:
        super().__init__(d, client)
        from ..model_loaders.submission_ASYNC import load_submission  # Avoid cyclic import
        my_load_submission = lambda d: load_submission(d=d, client=client)
        self.__original: Optional[Submission] = self._load_original(
            d=d,
            load_submission=my_load_submission,
        )

CrossPost = CrosspostSubmission
