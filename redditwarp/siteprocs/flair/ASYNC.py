
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable, Sequence, Tuple
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.flair import FlairTemplate, FlairTemplateChoices, UserFlairAssociation

import csv
from io import StringIO

from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_chaining_async_iterator import CallChunkChainingAsyncIterator
from ...iterators.async_call_chunk import AsyncCallChunk
from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.paginators.flair_async1 import UserFlairAssociationAsyncPaginator
from ...model_loaders.flair import (
    load_variant2_flair_template,
    load_variant1_flair_template,
    load_flair_template_choices,
    load_user_flair_association,
)

class FlairProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client

    async def set_user_flair(self,
        sr: str,
        user: str,
        text: Optional[str],
        css_class: Optional[str] = None,
    ) -> None:
        def g() -> Iterable[tuple[str, str]]:
            yield ('name', user)
            if text is not None: yield ('text', text)
            if css_class is not None: yield ('css_class', css_class)

        await self._client.request('POST', f'/r/{sr}/api/flair', data=dict(g()))

    async def set_post_flair(self,
        sr: str,
        subm: int,
        text: Optional[str],
        css_class: Optional[str] = None,
    ) -> None:
        full_id36 = 't3_' + to_base36(subm)

        def g() -> Iterable[tuple[str, str]]:
            yield ('link', full_id36)
            if text is not None: yield ('text', text)
            if css_class is not None: yield ('css_class', css_class)

        await self._client.request('POST', f'/r/{sr}/api/flair', data=dict(g()))

    def bulk_set_user_flairs(self,
        sr: str,
        items: Iterable[Tuple[str, str, str]],
    ) -> CallChunkChainingAsyncIterator[bool]:
        async def mass_update_user_flairs(items: Sequence[Tuple[str, str, str]]) -> Sequence[bool]:
            sio = StringIO()
            csv.writer(sio).writerows(items)
            s = sio.getvalue()
            root = await self._client.request('POST', f'/r/{sr}/api/flaircsv', files={'flair_csv': s})
            return [d['ok'] for d in root]

        itr = map(
            lambda xs: AsyncCallChunk(mass_update_user_flairs, xs),
            chunked(items, 100),
        )
        return CallChunkChainingAsyncIterator(itr)

    async def _create_or_update_flair_template(self,
        sr: str,
        flair_type: str,
        *,
        uuid: Optional[str] = None,
        text: Optional[str] = None,
        css_class: Optional[str] = None,
        bg_color: Optional[str] = None,
        fg_color_scheme: Optional[str] = None,
        mod_only: Optional[bool] = None,
        text_editable: Optional[bool] = None,
        allowable_content: Optional[str] = None,
        max_emojis: Optional[int] = None,
    ) -> FlairTemplate:
        d = {'flair_type': flair_type}
        for k, v in (
            ('flair_template_id', uuid),
            ('text', text),
            ('css_class', css_class),
            ('background_color', bg_color),
            ('text_color', fg_color_scheme),
            ('mod_only', None if mod_only is None else '01'[mod_only]),
            ('text_editable', None if text_editable is None else '01'[text_editable]),
            ('allowable_content', allowable_content),
            ('max_emojis', str(max_emojis)),
        ):
            if v is not None:
                d[k] = v
        root = await self._client.request('POST', f'/r/{sr}/api/flairtemplate_v2', data=d)
        return load_variant2_flair_template(root)

    async def create_user_flair_template(self,
        sr: str,
        *,
        text: Optional[str] = None,
        css_class: Optional[str] = None,
        bg_color: Optional[str] = None,
        fg_color_scheme: Optional[str] = None,
        mod_only: Optional[bool] = None,
        text_editable: Optional[bool] = None,
        allowable_content: Optional[str] = None,
        max_emojis: Optional[int] = None,
    ) -> FlairTemplate:
        return await self._create_or_update_flair_template(
            sr,
            flair_type='USER_FLAIR',
            text=text,
            css_class=css_class,
            bg_color=bg_color,
            fg_color_scheme=fg_color_scheme,
            mod_only=mod_only,
            text_editable=text_editable,
            allowable_content=allowable_content,
            max_emojis=max_emojis,
        )

    async def create_post_flair_template(self,
        sr: str,
        *,
        text: Optional[str] = None,
        css_class: Optional[str] = None,
        bg_color: Optional[str] = None,
        fg_color_scheme: Optional[str] = None,
        mod_only: Optional[bool] = None,
        text_editable: Optional[bool] = None,
        allowable_content: Optional[str] = None,
        max_emojis: Optional[int] = None,
    ) -> FlairTemplate:
        return await self._create_or_update_flair_template(
            sr,
            flair_type='LINK_FLAIR',
            text=text,
            css_class=css_class,
            bg_color=bg_color,
            fg_color_scheme=fg_color_scheme,
            mod_only=mod_only,
            text_editable=text_editable,
            allowable_content=allowable_content,
            max_emojis=max_emojis,
        )

    async def update_user_flair_template(self,
        sr: str,
        uuid: str,
        *,
        text: Optional[str] = None,
        css_class: Optional[str] = None,
        bg_color: Optional[str] = None,
        fg_color_scheme: Optional[str] = None,
        mod_only: Optional[bool] = None,
        text_editable: Optional[bool] = None,
        allowable_content: Optional[str] = None,
        max_emojis: Optional[int] = None,
    ) -> FlairTemplate:
        return await self._create_or_update_flair_template(
            sr,
            flair_type='USER_FLAIR',
            uuid=uuid,
            text=text,
            css_class=css_class,
            bg_color=bg_color,
            fg_color_scheme=fg_color_scheme,
            mod_only=mod_only,
            text_editable=text_editable,
            allowable_content=allowable_content,
            max_emojis=max_emojis,
        )

    async def update_post_flair_template(self,
        sr: str,
        uuid: str,
        *,
        text: Optional[str] = None,
        css_class: Optional[str] = None,
        bg_color: Optional[str] = None,
        fg_color_scheme: Optional[str] = None,
        mod_only: Optional[bool] = None,
        text_editable: Optional[bool] = None,
        allowable_content: Optional[str] = None,
        max_emojis: Optional[int] = None,
    ) -> FlairTemplate:
        return await self._create_or_update_flair_template(
            sr,
            flair_type='LINK_FLAIR',
            uuid=uuid,
            text=text,
            css_class=css_class,
            bg_color=bg_color,
            fg_color_scheme=fg_color_scheme,
            mod_only=mod_only,
            text_editable=text_editable,
            allowable_content=allowable_content,
            max_emojis=max_emojis,
        )

    async def delete_flair_template(self, sr: str, uuid: str) -> None:
        await self._client.request('POST', f'/r/{sr}/api/deleteflairtemplate', data={'flair_template_id': uuid})

    async def delete_all_user_flair_templates(self, sr: str) -> None:
        await self._client.request('POST', f'/r/{sr}/api/clearflairtemplates', data={'flair_type': 'USER_FLAIR'})

    async def delete_all_post_flair_templates(self, sr: str) -> None:
        await self._client.request('POST', f'/r/{sr}/api/clearflairtemplates', data={'flair_type': 'LINK_FLAIR'})

    async def retrieve_user_flair_templates(self, sr: str) -> Sequence[FlairTemplate]:
        root = await self._client.request('GET', f'/r/{sr}/api/user_flair_v2')
        return [load_variant1_flair_template(d) for d in root]

    async def retrieve_post_flair_templates(self, sr: str) -> Sequence[FlairTemplate]:
        root = await self._client.request('GET', f'/r/{sr}/api/link_flair_v2')
        return [load_variant1_flair_template(d) for d in root]

    async def reorder_user_flair_templates(self, sr: str, order: Sequence[str]) -> None:
        params = {'subreddit': sr, 'flair_type': 'USER_FLAIR'}
        await self._client.request('PATCH', '/api/flair_template_order', params=params, json=order)

    async def reorder_post_flair_templates(self, sr: str, order: Sequence[str]) -> None:
        params = {'subreddit': sr, 'flair_type': 'LINK_FLAIR'}
        await self._client.request('PATCH', '/api/flair_template_order', params=params, json=order)

    async def assign_user_flair_template(self,
        sr: str,
        user: str,
        uuid: str,
        *,
        text: Optional[str] = None,
    ) -> None:
        d = {
            'name': user,
            'flair_template_id': uuid,
        }
        if text is not None:
            d['text'] = text
        await self._client.request('POST', f'/r/{sr}/api/selectflair', data=d)

    async def assign_post_flair_template(self,
        sr: str,
        subm: int,
        uuid: str,
        *,
        text: Optional[str] = None,
    ) -> None:
        full_id36 = 't3_' + to_base36(subm)
        d = {
            'link': full_id36,
            'flair_template_id': uuid,
        }
        if text is not None:
            d['text'] = text
        await self._client.request('POST', f'/r/{sr}/api/selectflair', data=d)

    async def assign_user_flair(self,
        sr: str,
        user: str,
        text: Optional[str],
        css_class: Optional[str] = None,
        *,
        bg_color: Optional[str] = None,
        fg_color_scheme: Optional[str] = None,
    ) -> None:
        d = {'name': user}
        for k, v in (
            ('text', text),
            ('css_class', css_class),
            ('background_color', bg_color),
            ('text_color', fg_color_scheme),
        ):
            if v is not None:
                d[k] = v
        await self._client.request('POST', f'/r/{sr}/api/selectflair', data=d)

    async def assign_post_flair(self,
        sr: str,
        subm: int,
        text: Optional[str],
        css_class: Optional[str] = None,
        *,
        bg_color: Optional[str] = None,
        fg_color_scheme: Optional[str] = None,
    ) -> None:
        full_id36 = 't3_' + to_base36(subm)
        d = {'link': full_id36}
        for k, v in (
            ('text', text),
            ('css_class', css_class),
            ('background_color', bg_color),
            ('text_color', fg_color_scheme),
        ):
            if v is not None:
                d[k] = v
        await self._client.request('POST', f'/r/{sr}/api/selectflair', data=d)

    async def configure_subreddit_flair_settings(self,
        sr: str,
        *,
        user_enabled: Optional[bool] = False,
        user_position: Optional[str] = '',
        user_self_assign: Optional[bool] = False,
        post_position: Optional[str] = '',
        post_self_assign: Optional[bool] = False,
    ) -> None:
        def g() -> Iterable[tuple[str, str]]:
            if user_enabled is not None:
                yield ('flair_enabled', '01'[user_enabled])
            if user_position is not None:
                yield ('flair_position', user_position)
            if user_self_assign is not None:
                yield ('flair_self_assign_enabled', '01'[user_self_assign])
            if post_position is not None:
                yield ('link_flair_position', post_position)
            if post_self_assign is not None:
                yield ('link_flair_self_assign_enabled', '01'[post_self_assign])

        await self._client.request('POST', f'/r/{sr}/api/flairconfig', data=dict(g()))

    async def get_user_flair_template_choices(self, sr: str) -> FlairTemplateChoices:
        root = await self._client.request('POST', f'/r/{sr}/api/flairselector')
        return load_flair_template_choices(root)

    async def get_post_flair_template_choices(self, sr: str) -> FlairTemplateChoices:
        root = await self._client.request('POST', f'/r/{sr}/api/flairselector', data={'is_newlink': '1'})
        return load_flair_template_choices(root)

    async def get_user_flair_association(self, sr: str, user: str) -> Optional[UserFlairAssociation]:
        params = {'name': user, 'limit': '1'}
        root = await self._client.request('GET', f'/r/{sr}/api/flairlist', params=params)
        users_data = root['users']
        if not users_data:
            return None
        user_data = users_data[0]
        if user_data['user'].lower() != user.lower():
            return None
        return load_user_flair_association(user_data)

    def get_user_flair_associations(self,
        sr: str,
        amount: Optional[int] = None,
    ) -> ImpartedPaginatorChainingAsyncIterator[UserFlairAssociationAsyncPaginator, UserFlairAssociation]:
        p = UserFlairAssociationAsyncPaginator(self._client, f'/r/{sr}/api/flairlist')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    async def show_my_flair(self, sr: str) -> None:
        await self._client.request('GET', f'/r/{sr}/api/setflairenabled', params={'flair_enabled': '1'})

    async def hide_my_flair(self, sr: str) -> None:
        await self._client.request('GET', f'/r/{sr}/api/setflairenabled', params={'flair_enabled': '0'})
