
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable, Sequence, Tuple
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.flair import FlairTemplate, FlairChoices, UserFlairAssociation

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
    load_flair_choices,
    load_user_flair_association,
)

class FlairProcedures:
    def __init__(self, client: Client):
        self._client = client

    async def assign_user_flair(self, sr_name: str, name: str, text: Optional[str], css_class: Optional[str]) -> None:
        d = {'name': name}
        if text is not None:
            d['text'] = text
        if css_class is not None:
            d['css_class'] = css_class
        await self._client.request('POST', f'/r/{sr_name}/api/flair', data=d)

    async def assign_post_flair(self, sr_name: str, submission_id: int, text: Optional[str], css_class: Optional[str]) -> None:
        full_id36 = 't3_' + to_base36(submission_id)
        d = {'link': full_id36}
        if text is not None:
            d['text'] = text
        if css_class is not None:
            d['css_class'] = css_class
        await self._client.request('POST', f'/r/{sr_name}/api/flair', data=d)

    async def revoke_user_flair(self, sr_name: str, name: str) -> None:
        await self._client.request('POST', f'/r/{sr_name}/api/flair', data=dict(name=name))

    async def revoke_post_flair(self, sr_name: str, submission_id: int) -> None:
        full_id36 = 't3_' + to_base36(submission_id)
        await self._client.request('POST', f'/r/{sr_name}/api/flair', data=dict(link=full_id36))

    def bulk_update_user_flairs(self,
        sr_name: str,
        data: Iterable[Tuple[str, str, str]],
    ) -> CallChunkChainingAsyncIterator[bool]:
        async def mass_update_user_flairs(data: Sequence[Tuple[str, str, str]]) -> Sequence[bool]:
            sio = StringIO()
            csv.writer(sio).writerows(data)
            s = sio.getvalue()
            root = await self._client.request('POST', f'/r/{sr_name}/api/flaircsv', data={'flair_csv': s})
            return [i['ok'] for i in root]

        itr = map(
            lambda xs: AsyncCallChunk(mass_update_user_flairs, xs),
            chunked(data, 100),
        )
        return CallChunkChainingAsyncIterator(itr)

    async def _create_or_update_flair_template(self,
        sr_name: str,
        *,
        flair_type: str,
        uuid: Optional[str] = None,
        text: Optional[str] = None,
        allowable_content: Optional[str] = None,
        bg_color: Optional[str] = None,
        css_class: Optional[str] = None,
        fg_light_or_dark: Optional[str] = None,
        text_editable: Optional[bool] = None,
        max_emojis: Optional[int] = None,
        mod_only: Optional[bool] = None,
    ) -> FlairTemplate:
        d = {'flair_type': flair_type}
        for k, v in (
            ('flair_template_id', uuid),
            ('text', text),
            ('allowable_content', allowable_content),
            ('background_color', bg_color),
            ('css_class', css_class),
            ('text_color', fg_light_or_dark),
            ('text_editable', None if text_editable is None else '01'[text_editable]),
            ('max_emojis', str(max_emojis)),
            ('mod_only', None if mod_only is None else '01'[mod_only]),
        ):
            if v is not None:
                d[k] = v
        root = await self._client.request('POST', f'/r/{sr_name}/api/flairtemplate_v2', data=d)
        return load_variant2_flair_template(root)

    async def create_user_flair_template(self,
        sr_name: str,
        *,
        text: Optional[str] = None,
        allowable_content: Optional[str] = None,
        bg_color: Optional[str] = None,
        css_class: Optional[str] = None,
        fg_light_or_dark: Optional[str] = None,
        text_editable: Optional[bool] = None,
        max_emojis: Optional[int] = None,
        mod_only: Optional[bool] = None,
    ) -> FlairTemplate:
        return await self._create_or_update_flair_template(
            sr_name,
            flair_type='USER_FLAIR',
            text=text,
            allowable_content=allowable_content,
            bg_color=bg_color,
            css_class=css_class,
            fg_light_or_dark=fg_light_or_dark,
            text_editable=text_editable,
            max_emojis=max_emojis,
            mod_only=mod_only,
        )

    async def create_post_flair_template(self,
        sr_name: str,
        *,
        text: Optional[str] = None,
        allowable_content: Optional[str] = None,
        bg_color: Optional[str] = None,
        css_class: Optional[str] = None,
        fg_light_or_dark: Optional[str] = None,
        text_editable: Optional[bool] = None,
        max_emojis: Optional[int] = None,
        mod_only: Optional[bool] = None,
    ) -> FlairTemplate:
        return await self._create_or_update_flair_template(
            sr_name,
            flair_type='POST_FLAIR',
            text=text,
            allowable_content=allowable_content,
            bg_color=bg_color,
            css_class=css_class,
            fg_light_or_dark=fg_light_or_dark,
            text_editable=text_editable,
            max_emojis=max_emojis,
            mod_only=mod_only,
        )

    async def update_user_flair_template(self,
        sr_name: str,
        uuid: str,
        *,
        text: Optional[str] = None,
        allowable_content: Optional[str] = None,
        bg_color: Optional[str] = None,
        css_class: Optional[str] = None,
        fg_light_or_dark: Optional[str] = None,
        text_editable: Optional[bool] = None,
        max_emojis: Optional[int] = None,
        mod_only: Optional[bool] = None,
    ) -> FlairTemplate:
        return await self._create_or_update_flair_template(
            sr_name,
            flair_type='USER_FLAIR',
            uuid=uuid,
            text=text,
            allowable_content=allowable_content,
            bg_color=bg_color,
            css_class=css_class,
            fg_light_or_dark=fg_light_or_dark,
            text_editable=text_editable,
            max_emojis=max_emojis,
            mod_only=mod_only,
        )

    async def update_post_flair_template(self,
        sr_name: str,
        uuid: str,
        *,
        text: Optional[str] = None,
        allowable_content: Optional[str] = None,
        bg_color: Optional[str] = None,
        css_class: Optional[str] = None,
        fg_light_or_dark: Optional[str] = None,
        text_editable: Optional[bool] = None,
        max_emojis: Optional[int] = None,
        mod_only: Optional[bool] = None,
    ) -> FlairTemplate:
        return await self._create_or_update_flair_template(
            sr_name,
            flair_type='USER_FLAIR',
            uuid=uuid,
            text=text,
            allowable_content=allowable_content,
            bg_color=bg_color,
            css_class=css_class,
            fg_light_or_dark=fg_light_or_dark,
            text_editable=text_editable,
            max_emojis=max_emojis,
            mod_only=mod_only,
        )

    async def assign_user_flair_template(self,
        sr_name: str,
        name: str,
        uuid: Optional[str],
        *,
        text: Optional[str] = None,
        css_class: Optional[str] = None,
        bg_color: Optional[str] = None,
        fg_light_or_dark: Optional[str] = None,
    ) -> None:
        d = {'name': name}
        for k, v in (
            ('flair_template_id', uuid),
            ('text', text),
            ('css_class', css_class),
            ('background_color', bg_color),
            ('text_color', fg_light_or_dark),
        ):
            if v is not None:
                d[k] = v
        await self._client.request('POST', f'/r/{sr_name}/api/selectflair', data=d)

    async def assign_post_flair_template(self,
        sr_name: str,
        submission_id: int,
        uuid: Optional[str],
        *,
        text: Optional[str] = None,
        css_class: Optional[str] = None,
        bg_color: Optional[str] = None,
        fg_light_or_dark: Optional[str] = None,
    ) -> None:
        full_id36 = 't3_' + to_base36(submission_id)
        d = {'link': full_id36}
        for k, v in (
            ('flair_template_id', uuid),
            ('text', text),
            ('css_class', css_class),
            ('background_color', bg_color),
            ('text_color', fg_light_or_dark),
        ):
            if v is not None:
                d[k] = v
        await self._client.request('POST', f'/r/{sr_name}/api/selectflair', data=d)

    async def revoke_user_flair_template(self, sr_name: str, name: str) -> None:
        await self._client.request('POST', f'/r/{sr_name}/api/selectflair', data=dict(name=name))

    async def revoke_post_flair_template(self, sr_name: str, submission_id: int) -> None:
        full_id36 = 't3_' + to_base36(submission_id)
        await self._client.request('POST', f'/r/{sr_name}/api/selectflair', data=dict(link=full_id36))

    async def delete_user_flair_template(self, sr_name: str, uuid: str) -> None:
        await self._client.request('POST', f'/r/{sr_name}/api/deleteflairtemplate',
                data=dict(flair_template_id=uuid))

    async def delete_post_flair_template(self, sr_name: str, uuid: str) -> None:
        await self.delete_user_flair_template(sr_name, uuid)

    async def delete_all_user_flair_templates(self, sr_name: str) -> None:
        await self._client.request('POST', f'/r/{sr_name}/api/clearflairtemplates', data={'flair_type': 'USER_FLAIR'})

    async def delete_all_post_flair_templates(self, sr_name: str) -> None:
        await self._client.request('POST', f'/r/{sr_name}/api/clearflairtemplates', data={'flair_type': 'POST_FLAIR'})

    async def configure_subreddit_flair_settings(self,
        sr_name: str,
        *,
        user_flair_enabled: Optional[bool],
        user_flair_position: Optional[str],
        user_flair_self_assign: Optional[bool],
        post_flair_position: Optional[str],
        post_flair_self_assign: Optional[bool],
    ) -> None:
        def g() -> Iterable[tuple[str, str]]:
            if user_flair_enabled is not None:
                yield ('flair_enabled', '01'[user_flair_enabled])
            if user_flair_position is not None:
                yield ('flair_position', user_flair_position)
            if user_flair_self_assign is not None:
                yield ('flair_self_assign_enabled', '01'[user_flair_self_assign])
            if post_flair_position is not None:
                yield ('link_flair_position', post_flair_position)
            if post_flair_self_assign is not None:
                yield ('link_flair_self_assign_enabled', '01'[post_flair_self_assign])

        await self._client.request('POST', f'/r/{sr_name}/api/flairconfig', data=dict(g()))

    async def reorder_user_flair_templates(self, sr_name: str, order: Sequence[str]) -> None:
        params = {'subreddit': sr_name, 'flair_type': 'USER_FLAIR'}
        await self._client.request('PATCH', '/api/flair_template_order', params=params, json=order)

    async def reorder_post_flair_templates(self, sr_name: str, order: Sequence[str]) -> None:
        params = {'subreddit': sr_name, 'flair_type': 'POST_FLAIR'}
        await self._client.request('PATCH', '/api/flair_template_order', params=params, json=order)

    async def get_user_flair_templates(self, sr_name: str) -> Sequence[FlairTemplate]:
        root = await self._client.request('GET', f'/r/{sr_name}/api/user_flair_v2')
        return [load_variant1_flair_template(i) for i in root]

    async def get_post_flair_templates(self, sr_name: str) -> Sequence[FlairTemplate]:
        root = await self._client.request('GET', f'/r/{sr_name}/api/link_flair_v2')
        return [load_variant1_flair_template(i) for i in root]

    async def get_user_flair_choices(self, sr_name: str, name: Optional[str]) -> Optional[FlairChoices]:
        d = {}
        if name is not None:
            d['name'] = name
        root = await self._client.request('POST', f'/r/{sr_name}/api/flairselector', data=d)
        if root == '{}':
            return None
        return load_flair_choices(root)

    async def get_post_flair_choices(self, sr_name: str, submission_id: Optional[int]) -> Optional[FlairChoices]:
        d = {'is_newlink': '1'}
        if submission_id is not None:
            full_id36 = to_base36(submission_id)
            d['link'] = full_id36
        root = await self._client.request('POST', f'/r/{sr_name}/api/flairselector', data=d)
        if root == '{}':
            return None
        return load_flair_choices(root)

    async def get_user_flair_association(self, sr_name: str, name: str) -> Optional[UserFlairAssociation]:
        params = {'name': name, 'limit': '1'}
        root = await self._client.request('GET', f'/r/{sr_name}/api/flairlist', params=params)
        users_data = root['users']
        if not users_data:
            return None
        user_data = users_data[0]
        if user_data['user'].lower() != name.lower():
            return None
        return load_user_flair_association(user_data)

    def get_user_flair_associations(self,
        sr_name: str,
        amount: Optional[int] = None,
    ) -> ImpartedPaginatorChainingAsyncIterator[UserFlairAssociationAsyncPaginator, UserFlairAssociation]:
        p = UserFlairAssociationAsyncPaginator(self._client, f'/r/{sr_name}/api/flairlist')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    async def show_my_flair(self, sr_name: str) -> None:
        await self._client.request('GET', f'/r/{sr_name}/api/setflairenabled', params={'flair_enabled': '1'})

    async def hide_my_flair(self, sr_name: str) -> None:
        await self._client.request('GET', f'/r/{sr_name}/api/setflairenabled', params={'flair_enabled': '0'})
