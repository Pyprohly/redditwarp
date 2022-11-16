
from __future__ import annotations
from typing import TYPE_CHECKING, IO, Optional, Sequence, Any
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.widget.ASYNC import (
        TextAreaWidget,
        ButtonWidget,
        ImageWidget,
        CommunityListWidget,
        CalendarWidget,
        PostFlairWidget,
        CustomCSSWidget,
        CommunityDetailsWidget,
        ModeratorListWidget,
        RulesWidget,
        MenuBar,
    )
    from ...dtos.widget.button import (
        HoverState,
        TextHoverState,
        ImageHoverState,
        Button,
        TextButton,
        ImageButton,
    )
    from ...dtos.widget.custom_css import ImageInfo as CustomCSSWidgetImageInfo
    from ...dtos.widget.image import ImageInfo as ImageWidgetImageInfo
    from ...dtos.widget.menu_bar import (
        Tab,
        LinkTab,
        SubmenuTab,
    )

from functools import cached_property

from ...http.payload import guess_mimetype_from_filename
from ...models.widget import WidgetImageUploadLease
from ...models.widget.ASYNC import WidgetList
from ...model_loaders.widget import load_widget_image_upload_lease
from ...model_loaders.widget_ASYNC import (
    load_widget,
    load_text_area_widget,
    load_button_widget,
    load_image_widget,
    load_community_list_widget,
    load_calendar_widget,
    load_post_flair_widget,
    load_custom_css_widget,
    load_community_details_widget,
    load_moderator_list_widget,
    load_rules_widget,
    load_menu_bar,
)


def _build_text_area_widget_json(
    *,
    header_color: str,
    background_color: str,
    title: str,
    text: str,
) -> Any:
    return {
        'kind': 'textarea',
        'styles': {'headerColor': header_color, 'backgroundColor': background_color},
        'shortName': title,
        'text': text,
    }

def _build_button_widget_json(
    *,
    header_color: str,
    background_color: str,
    title: str,
    description: str,
    buttons: Sequence[Button],
) -> Any:
    buttons_json: list[dict[str, Any]] = []
    for button in buttons:
        button_json: Optional[dict[str, Any]] = None
        if isinstance(button, TextButton):
            button_json = {
                'kind': 'text',
                'text': button.label,
                'url': button.link,
                'textColor': button.text_color,
                'fillColor': button.fill_color,
                'color': button.stroke_color,
            }
        elif isinstance(button, ImageButton):
            button_json = {
                'kind': 'image',
                'text': button.label,
                'linkUrl': button.link,
                'url': button.image_url,
                'width': button.image_size[0],
                'height': button.image_size[1],
            }
        else:
            if type(button) is Button:
                raise ValueError('a subclass of Button must be provided')
            raise Exception

        hs = button.hover_state
        if hs is not None:
            if isinstance(hs, TextHoverState):
                button_json['hoverState'] = {
                    'kind': 'text',
                    'text': hs.label,
                    'textColor': hs.text_color,
                    'fillColor': hs.fill_color,
                    'color': hs.stroke_color,
                }
            elif isinstance(hs, ImageHoverState):
                button_json['hoverState'] = {
                    'kind': 'image',
                    'url': hs.image_url,
                    'width': hs.image_size[0],
                    'height': hs.image_size[1],
                }
            else:
                if type(hs) is HoverState:
                    raise ValueError('a subclass of HoverState must be provided')
                raise Exception

        buttons_json.append(button_json)

    return {
        'kind': 'button',
        'styles': {'headerColor': header_color, 'backgroundColor': background_color},
        'shortName': title,
        'description': description,
        'buttons': buttons_json,
    }

def _build_image_widget_json(
    *,
    header_color: str,
    background_color: str,
    title: str,
    items: Sequence[ImageWidgetImageInfo],
) -> Any:
    return {
        'kind': 'image',
        'styles': {'headerColor': header_color, 'backgroundColor': background_color},
        'shortName': title,
        'data': [
            {
                'url': image_info.url,
                'width': image_info.size[0],
                'height': image_info.size[1],
                'linkUrl': image_info.link,
            }
            for image_info in items
        ],
    }

def _build_community_list_widget_json(
    *,
    header_color: str,
    background_color: str,
    title: str,
    items: Sequence[str],
) -> Any:
    return {
        'kind': 'community-list',
        'styles': {'headerColor': header_color, 'backgroundColor': background_color},
        'shortName': title,
        'data': list(items),
    }

def _build_calendar_widget_json(
    *,
    header_color: str,
    background_color: str,
    title: str,
    google_calendar_id: str,
    requires_sync: bool,
    num_events: int,
    show_title: bool,
    show_description: bool,
    show_location: bool,
    show_date: bool,
    show_time: bool,
) -> Any:
    return {
        'kind': 'calendar',
        'styles': {'headerColor': header_color, 'backgroundColor': background_color},
        'shortName': title,
        'googleCalendarId': google_calendar_id,
        'requiresSync': requires_sync,
        'configuration': {
            'numEvents': num_events,
            'showTitle': show_title,
            'showDescription': show_description,
            'showLocation': show_location,
            'showDate': show_date,
            'showTime': show_time,
        },
    }

def _build_post_flair_widget_json(
    *,
    header_color: str,
    background_color: str,
    title: str,
    display: str,
    order: Sequence[str],
) -> Any:
    return {
        'kind': 'post-flair',
        'styles': {'headerColor': header_color, 'backgroundColor': background_color},
        'shortName': title,
        'display': display,
        'order': list(order),
    }

def _build_custom_css_widget_json(
    *,
    header_color: str,
    background_color: str,
    title: str,
    text: str,
    css: str,
    height: Optional[int],
    image_data: Sequence[CustomCSSWidgetImageInfo],
) -> Any:
    return {
        'kind': 'custom',
        'styles': {'headerColor': header_color, 'backgroundColor': background_color},
        'shortName': title,
        'text': text,
        'css': css,
        'height': height,
        'imageData': [
            {
                'url': image_info.url,
                'width': image_info.width,
                'height': image_info.height,
                'name': image_info.name,
            }
            for image_info in image_data
        ],
    }

def _build_menu_bar_json(
    *,
    show_wiki: bool,
    tabs: Sequence[Tab],
) -> Any:
    tabs_json: list[dict[str, Any]] = []
    for tab in tabs:
        tab_json: Optional[dict[str, Any]] = None
        if isinstance(tab, LinkTab):
            tab_json = {'text': tab.label, 'url': tab.link}
        elif isinstance(tab, SubmenuTab):
            tab_json = {
                'text': tab.label,
                'children': [
                    {'text': smi.label, 'url': smi.link}
                    for smi in tab.items
                ],
            }
        else:
            if type(tab) is Tab:
                raise ValueError('a subclass of Tab must be provided')
            raise Exception

        tabs_json.append(tab_json)

    return {
        'kind': 'menu',
        'showWiki': show_wiki,
        'data': tabs_json,
    }


class WidgetProcedures:
    def __init__(self, client: Client):
        self._client = client

    class _upload_image:
        def __init__(self, outer: WidgetProcedures) -> None:
            self._client = outer._client

        async def __call__(self, file: IO[bytes], *, sr: str) -> WidgetImageUploadLease:
            return await self.upload(file, sr=sr)

        async def obtain_upload_lease(self, *, sr: str, filename: str, mimetype: Optional[str] = None) -> WidgetImageUploadLease:
            if mimetype is None:
                mimetype = guess_mimetype_from_filename(filename)
            result = await self._client.request('POST', f'/api/v1/{sr}/emoji_asset_upload_s3',
                    data={'filepath': filename, 'mimetype': mimetype})
            return load_widget_image_upload_lease(result)

        async def deposit_file(self, file: IO[bytes], upload_lease: WidgetImageUploadLease, *,
                timeout: float = 1000) -> None:
            session = self._client.http.session
            resp = await session.request('POST', upload_lease.endpoint, data=upload_lease.fields,
                    files={'file': file}, timeout=timeout)
            resp.raise_for_status()

        async def upload(self, file: IO[bytes], *, sr: str, timeout: float = 1000) -> WidgetImageUploadLease:
            upload_lease = await self.obtain_upload_lease(filename=file.name, sr=sr)
            await self.deposit_file(file, upload_lease, timeout=timeout)
            return upload_lease

    upload_image: cached_property[_upload_image] = cached_property(_upload_image)

    class _create:
        def __init__(self, outer: WidgetProcedures) -> None:
            self._client = outer._client

        async def _invoke(self, sr: str, json: Any) -> Any:
            return await self._client.request('POST', f'/r/{sr}/api/widget', json=json)

        async def text_area(self,
            sr: str,
            *,
            header_color: str,
            background_color: str,
            title: str,
            text: str,
        ) -> TextAreaWidget:
            json = _build_text_area_widget_json(
                header_color=header_color,
                background_color=background_color,
                title=title,
                text=text,
            )
            root = await self._invoke(sr, json=json)
            return load_text_area_widget(root)

        async def button(self,
            sr: str,
            *,
            header_color: str,
            background_color: str,
            title: str,
            description: str,
            buttons: Sequence[Button],
        ) -> ButtonWidget:
            json = _build_button_widget_json(
                header_color=header_color,
                background_color=background_color,
                title=title,
                description=description,
                buttons=buttons,
            )
            root = await self._invoke(sr, json=json)
            return load_button_widget(root)

        async def image(self,
            sr: str,
            *,
            header_color: str,
            background_color: str,
            title: str,
            items: Sequence[ImageWidgetImageInfo],
        ) -> ImageWidget:
            json = _build_image_widget_json(
                header_color=header_color,
                background_color=background_color,
                title=title,
                items=items,
            )
            root = await self._invoke(sr, json=json)
            return load_image_widget(root)

        async def community_list(self,
            sr: str,
            *,
            header_color: str,
            background_color: str,
            title: str,
            items: Sequence[str],
        ) -> CommunityListWidget:
            json = _build_community_list_widget_json(
                header_color=header_color,
                background_color=background_color,
                title=title,
                items=items,
            )
            root = await self._invoke(sr, json=json)
            return load_community_list_widget(root)

        async def calendar(self,
            sr: str,
            *,
            header_color: str,
            background_color: str,
            title: str,
            google_calendar_id: str,
            requires_sync: bool,
            num_events: int,
            show_title: bool,
            show_description: bool,
            show_location: bool,
            show_date: bool,
            show_time: bool,
        ) -> CalendarWidget:
            json = _build_calendar_widget_json(
                header_color=header_color,
                background_color=background_color,
                title=title,
                google_calendar_id=google_calendar_id,
                requires_sync=requires_sync,
                num_events=num_events,
                show_title=show_title,
                show_description=show_description,
                show_location=show_location,
                show_date=show_date,
                show_time=show_time,
            )
            root = await self._invoke(sr, json=json)
            return load_calendar_widget(root)

        async def post_flair(self,
            sr: str,
            *,
            header_color: str,
            background_color: str,
            title: str,
            display: str,
            order: Sequence[str],
        ) -> PostFlairWidget:
            json = _build_post_flair_widget_json(
                header_color=header_color,
                background_color=background_color,
                title=title,
                display=display,
                order=order,
            )
            root = await self._invoke(sr, json=json)
            return load_post_flair_widget(root)

        async def custom_css(self,
            sr: str,
            *,
            header_color: str,
            background_color: str,
            title: str,
            text: str,
            css: str,
            height: Optional[int],
            image_data: Sequence[CustomCSSWidgetImageInfo],
        ) -> CustomCSSWidget:
            json = _build_custom_css_widget_json(
                header_color=header_color,
                background_color=background_color,
                title=title,
                text=text,
                css=css,
                height=height,
                image_data=image_data,
            )
            root = await self._invoke(sr, json=json)
            return load_custom_css_widget(root)

    create: cached_property[_create] = cached_property(_create)

    class _update:
        def __init__(self, outer: WidgetProcedures) -> None:
            self._client = outer._client

        async def _invoke(self, sr: str, idt: str, json: Any) -> Any:
            return await self._client.request('PUT', f'/r/{sr}/api/widget/{idt}', json=json)

        async def text_area(self,
            sr: str,
            idt: str,
            *,
            header_color: str,
            background_color: str,
            title: str,
            text: str,
        ) -> TextAreaWidget:
            json = _build_text_area_widget_json(
                header_color=header_color,
                background_color=background_color,
                title=title,
                text=text,
            )
            root = await self._invoke(sr, idt, json=json)
            return load_text_area_widget(root)

        async def button(self,
            sr: str,
            idt: str,
            *,
            header_color: str,
            background_color: str,
            title: str,
            description: str,
            buttons: Sequence[Button],
        ) -> ButtonWidget:
            json = _build_button_widget_json(
                header_color=header_color,
                background_color=background_color,
                title=title,
                description=description,
                buttons=buttons,
            )
            root = await self._invoke(sr, idt, json=json)
            return load_button_widget(root)

        async def image(self,
            sr: str,
            idt: str,
            *,
            header_color: str,
            background_color: str,
            title: str,
            items: Sequence[ImageWidgetImageInfo],
        ) -> ImageWidget:
            json = _build_image_widget_json(
                header_color=header_color,
                background_color=background_color,
                title=title,
                items=items,
            )
            root = await self._invoke(sr, idt, json=json)
            return load_image_widget(root)

        async def community_list(self,
            sr: str,
            idt: str,
            *,
            header_color: str,
            background_color: str,
            title: str,
            items: Sequence[str],
        ) -> CommunityListWidget:
            json = _build_community_list_widget_json(
                header_color=header_color,
                background_color=background_color,
                title=title,
                items=items,
            )
            root = await self._invoke(sr, idt, json=json)
            return load_community_list_widget(root)

        async def calendar(self,
            sr: str,
            idt: str,
            *,
            header_color: str,
            background_color: str,
            title: str,
            google_calendar_id: str,
            requires_sync: bool,
            num_events: int,
            show_title: bool,
            show_description: bool,
            show_location: bool,
            show_date: bool,
            show_time: bool,
        ) -> CalendarWidget:
            json = _build_calendar_widget_json(
                header_color=header_color,
                background_color=background_color,
                title=title,
                google_calendar_id=google_calendar_id,
                requires_sync=requires_sync,
                num_events=num_events,
                show_title=show_title,
                show_description=show_description,
                show_location=show_location,
                show_date=show_date,
                show_time=show_time,
            )
            root = await self._invoke(sr, idt, json=json)
            return load_calendar_widget(root)

        async def post_flair(self,
            sr: str,
            idt: str,
            *,
            header_color: str,
            background_color: str,
            title: str,
            display: str,
            order: Sequence[str],
        ) -> PostFlairWidget:
            json = _build_post_flair_widget_json(
                header_color=header_color,
                background_color=background_color,
                title=title,
                display=display,
                order=order,
            )
            root = await self._invoke(sr, idt, json=json)
            return load_post_flair_widget(root)

        async def custom_css(self,
            sr: str,
            idt: str,
            *,
            header_color: str,
            background_color: str,
            title: str,
            text: str,
            css: str,
            height: Optional[int],
            image_data: Sequence[CustomCSSWidgetImageInfo],
        ) -> CustomCSSWidget:
            json = _build_custom_css_widget_json(
                header_color=header_color,
                background_color=background_color,
                title=title,
                text=text,
                css=css,
                height=height,
                image_data=image_data,
            )
            root = await self._invoke(sr, idt, json=json)
            return load_custom_css_widget(root)

        async def community_details(self,
            sr: str,
            idt: str,
            *,
            header_color: str,
            background_color: str,
            title: str,
            subscriber_text: str,
            viewing_text: str,
        ) -> CommunityDetailsWidget:
            json = {
                'kind': 'post-flair',
                'styles': {'headerColor': header_color, 'backgroundColor': background_color},
                'shortName': title,
                'subscribersText': subscriber_text,
                'currentlyViewingText': viewing_text,
            }
            root = await self._invoke(sr, idt, json=json)
            return load_community_details_widget(root)

        async def moderator_list(self,
            sr: str,
            idt: str,
            *,
            header_color: str,
            background_color: str,
        ) -> ModeratorListWidget:
            json = {
                'kind': 'moderators',
                'styles': {'headerColor': header_color, 'backgroundColor': background_color},
            }
            root = await self._invoke(sr, idt, json=json)
            return load_moderator_list_widget(root)

        async def rules(self,
            sr: str,
            idt: str,
            *,
            header_color: str,
            background_color: str,
            title: str,
            display: str,
        ) -> RulesWidget:
            json = {
                'kind': 'post-flair',
                'styles': {'headerColor': header_color, 'backgroundColor': background_color},
                'shortName': title,
                'display': display,
            }
            root = await self._invoke(sr, idt, json=json)
            return load_rules_widget(root)

    update: cached_property[_update] = cached_property(_update)

    async def create_menu_bar_tabs(self,
        sr: str,
        *,
        show_wiki: bool,
        tabs: Sequence[Tab],
    ) -> MenuBar:
        json = _build_menu_bar_json(
            show_wiki=show_wiki,
            tabs=tabs,
        )
        root = await self._client.request('POST', f'/r/{sr}/api/widget', json=json)
        return load_menu_bar(root)

    async def update_menu_bar_tabs(self,
        sr: str,
        idt: str,
        *,
        show_wiki: bool,
        tabs: Sequence[Tab],
    ) -> MenuBar:
        json = _build_menu_bar_json(
            show_wiki=show_wiki,
            tabs=tabs,
        )
        root = await self._client.request('PUT', f'/r/{sr}/api/widget/{idt}', json=json)
        return load_menu_bar(root)

    async def retrieve(self, sr: str) -> WidgetList:
        root = await self._client.request('GET', f'/r/{sr}/api/widgets')
        layout = root['layout']

        order = layout['sidebar']['order']
        object_map = root['items']

        widgets = [load_widget(object_map[idt]) for idt in order]

        menu_bar = None
        topbar_order = layout['topbar']['order']
        if topbar_order:
            menu_bar = load_menu_bar(object_map[topbar_order[0]])

        id_card_widget_id = layout['idCardWidget']
        community_details_widget = load_community_details_widget(object_map[id_card_widget_id])

        moderator_list_widget = load_moderator_list_widget(object_map[layout['moderatorWidget']])

        subr_id36 = id_card_widget_id.rpartition('-')[2]
        rules_widget = None
        if (d := object_map.get(f'widget_rules-{subr_id36}')) is not None:
            rules_widget = load_rules_widget(d)

        return WidgetList(
            widgets=widgets,
            menu_bar=menu_bar,
            community_details_widget=community_details_widget,
            moderator_list_widget=moderator_list_widget,
            rules_widget=rules_widget,
        )

    async def delete(self, sr: str, idt: str) -> None:
        await self._client.request('DELETE', f'/r/{sr}/api/widget/{idt}')

    async def reorder(self, sr: str, order: Sequence[str]) -> None:
        await self._client.request('PATCH', f'/r/{sr}/api/widget_order/sidebar', json=list(order))
