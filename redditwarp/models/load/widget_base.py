
from __future__ import annotations
from typing import Mapping, Any, Optional

from ..widget import (
    ImageSize,
    ButtonWidgetNamespace,
    ImageWidgetNamespace,
    CommunityListWidgetNamespace,
    CalendarWidgetNamespace,
    PostFlairWidgetNamespace,
    CustomCSSWidgetNamespace,
    ModeratorListWidgetNamespace,
    RulesWidgetNamespace,
    MenuBarNamespace,
)
from ..widget_base import (
    BaseWidget,
    BaseTextAreaWidget,
    BaseButtonWidget,
    BaseImageWidget,
    BaseCommunityListWidget,
    BaseCalendarWidget,
    BasePostFlairWidget,
    BaseCustomCSSWidget,
    BaseCommunityDetailsWidget,
    BaseModeratorListWidget,
    BaseRulesWidget,
    BaseMenuBar,
)

def load_base_widget(d: Mapping[str, Any]) -> BaseWidget:
    kind = d['kind']
    if kind == 'textarea':
        return load_base_text_area_widget(d)
    elif kind == 'button':
        return load_base_button_widget(d)
    elif kind == 'image':
        return load_base_image_widget(d)
    elif kind == 'community-list':
        return load_base_community_list_widget(d)
    elif kind == 'calendar':
        return load_base_calendar_widget(d)
    elif kind == 'post-flair':
        return load_base_post_flair_widget(d)
    elif kind == 'custom':
        return load_base_custom_css_widget(d)
    elif kind == 'id-card':
        return load_base_community_details_widget(d)
    elif kind == 'moderators':
        return load_base_moderator_list_widget(d)
    elif kind == 'subreddit-rules':
        return load_base_rules_widget(d)
    raise Exception

def load_base_text_area_widget(d: Mapping[str, Any]) -> BaseTextAreaWidget:
    styles = d['styles']
    return BaseTextAreaWidget(
        d=d,
        idt=d['id'],
        kind=d['kind'],
        header_color=styles['headerColor'] or '',
        background_color=styles['backgroundColor'] or '',
        title=d['shortName'],
        text=d['text'],
        text_html=d['textHtml'],
    )

def load_base_button_widget(d: Mapping[str, Any]) -> BaseButtonWidget:
    styles = d['styles']
    buttons: list[ButtonWidgetNamespace.Button] = []
    for m in d['buttons']:
        hover_state: Optional[ButtonWidgetNamespace.HoverState] = None
        hs = m['hoverState']
        if hs is not None:
            if hs['kind'] == 'text':
                hover_state = ButtonWidgetNamespace.TextHoverState(
                    label=hs['text'],
                    text_color=hs.get('textColor', ''),
                    fill_color=hs.get('fillColor', ''),
                    stroke_color=hs['color'],
                )
            else:
                hover_state = ButtonWidgetNamespace.ImageHoverState(
                    image_url=hs['text'],
                    image_size=ImageSize(hs['width'], hs['height']),
                )

        btn: ButtonWidgetNamespace.Button
        if m['kind'] == 'text':
            btn = ButtonWidgetNamespace.TextButton(
                label=m['text'],
                link=m['url'],
                hover_state=hover_state,
                text_color=m.get('textColor', ''),
                fill_color=m.get('fillColor', ''),
                stroke_color=m['color'],
            )
            buttons.append(btn)
        else:
            btn = ButtonWidgetNamespace.ImageButton(
                label=m['text'],
                link=m['linkUrl'],
                hover_state=hover_state,
                image_url=m['url'],
                image_size=ImageSize(m['width'], m['height']),
            )
            buttons.append(btn)

    return BaseButtonWidget(
        d=d,
        idt=d['id'],
        kind=d['kind'],
        header_color=styles['headerColor'] or '',
        background_color=styles['backgroundColor'] or '',
        title=d['shortName'],
        description=d['description'],
        description_html=d['descriptionHtml'],
        buttons=buttons,
    )

def load_base_image_widget(d: Mapping[str, Any]) -> BaseImageWidget:
    styles = d['styles']
    image_items = [
        ImageWidgetNamespace.ImageWidgetItem(
            url=m['url'],
            size=ImageSize(m['width'], m['height']),
            link=m['linkUrl'] or '',
        )
        for m in d['data']
    ]
    return BaseImageWidget(
        d=d,
        idt=d['id'],
        kind=d['kind'],
        header_color=styles['headerColor'] or '',
        background_color=styles['backgroundColor'] or '',
        title=d['shortName'],
        items=image_items,
    )

def load_base_community_list_widget(d: Mapping[str, Any]) -> BaseCommunityListWidget:
    styles = d['styles']
    subr_items = [
        CommunityListWidgetNamespace.CommunityListWidgetItem(
            name=m['name'],
            subscribers=m['subscribers'],
            icon_img=m['iconUrl'],
            community_icon=m['communityIcon'],
            primary_color=m['primaryColor'],
            nsfw=m['isNSFW'],
        )
        for m in d['data']
    ]
    return BaseCommunityListWidget(
        d=d,
        idt=d['id'],
        kind=d['kind'],
        header_color=styles['headerColor'] or '',
        background_color=styles['backgroundColor'] or '',
        title=d['shortName'],
        items=subr_items,
    )

def load_base_calendar_widget(d: Mapping[str, Any]) -> BaseCalendarWidget:
    styles = d['styles']
    m = d['configuration']
    configuration = CalendarWidgetNamespace.CalendarWidgetConfiguration(
        num_events=m['numEvents'],
        show_title=m['showTitle'],
        show_description=m['showDescription'],
        show_location=m['showLocation'],
        show_date=m['showDate'],
        show_time=m['showTime'],
    )
    return BaseCalendarWidget(
        d=d,
        idt=d['id'],
        kind=d['kind'],
        header_color=styles['headerColor'] or '',
        background_color=styles['backgroundColor'] or '',
        title=d['shortName'],
        google_calendar_id=d['googleCalendarId'],
        requires_sync=d['requiresSync'],
        configuration=configuration,
    )

def load_base_post_flair_widget(d: Mapping[str, Any]) -> BasePostFlairWidget:
    styles = d['styles']
    templates = [
        PostFlairWidgetNamespace.PostFlairWidgetItem(
            d=m,
            uuid=m['templateId'],
            type=m['type'],
            text=m['text'],
            bg_color=m['backgroundColor'],
            fg_light_or_dark=m['textColor'],
        )
        for m in d['templates']
    ]
    return BasePostFlairWidget(
        d=d,
        idt=d['id'],
        kind=d['kind'],
        header_color=styles['headerColor'] or '',
        background_color=styles['backgroundColor'] or '',
        title=d['shortName'],
        display=d['display'],
        order=d['order'],
        templates=templates,
    )

def load_base_custom_css_widget(d: Mapping[str, Any]) -> BaseCustomCSSWidget:
    styles = d['styles']
    image_data = [
        CustomCSSWidgetNamespace.CustomCSSWidgetImageInfo(
            url=m['url'],
            width=m['width'],
            height=m['height'],
            name=m['name'],
        )
        for m in d['imageData']
    ]
    return BaseCustomCSSWidget(
        d=d,
        idt=d['id'],
        kind=d['kind'],
        header_color=styles['headerColor'] or '',
        background_color=styles['backgroundColor'] or '',
        title=d['shortName'],
        text=d['text'],
        css=d['css'],
        height=d['height'],
        image_data=image_data,
    )

def load_base_community_details_widget(d: Mapping[str, Any]) -> BaseCommunityDetailsWidget:
    styles = d['styles']
    return BaseCommunityDetailsWidget(
        d=d,
        idt=d['id'],
        kind=d['kind'],
        header_color=styles['headerColor'] or '',
        background_color=styles['backgroundColor'] or '',
        title=d['shortName'],
        public_description=d.get('description', ''),
        subscriber_text=d['subscribersText'],
        viewing_text=d['currentlyViewingText'],
        subscriber_count=d.get('subscribersCount', ''),
        viewing_count=d.get('currentlyViewingCount', ''),
    )

def load_base_moderator_list_widget(d: Mapping[str, Any]) -> BaseModeratorListWidget:
    styles = d['styles']
    mods = [
        ModeratorListWidgetNamespace.ModeratorInfo(
            name=m['name'],
            flair_type=m['authorFlairType'],
            flair_text=m['authorFlairText'] or '',
            flair_fg_light_or_dark=m['authorFlairTextColor'],
            flair_bg_color=m['authorFlairBackgroundColor'],
            flair_has_had_flair=m['authorFlairText'] is not None,
        )
        for m in d.get('mods', ())
    ]
    return BaseModeratorListWidget(
        d=d,
        idt=d['id'],
        kind=d['kind'],
        header_color=styles['headerColor'] or '',
        background_color=styles['backgroundColor'] or '',
        title='',
        mod_num=d.get('totalMods', 0),
        mods=mods,
    )

def load_base_rules_widget(d: Mapping[str, Any]) -> BaseRulesWidget:
    styles = d['styles']
    rules = [
        RulesWidgetNamespace.Rule(
            description=m['description'],
            description_html=m['descriptionHtml'],
            short_name=m['shortName'],
            violation_reason=m['violationReason'],
            created_ut=m['createdUtc'],
        )
        for m in d.get('data', ())
    ]
    return BaseRulesWidget(
        d=d,
        idt=d['id'],
        kind=d['kind'],
        header_color=styles['headerColor'] or '',
        background_color=styles['backgroundColor'] or '',
        title=d['shortName'],
        display=d['display'],
        rules=rules,
    )


def load_base_menu_bar(d: Mapping[str, Any]) -> BaseMenuBar:
    tabs: list[MenuBarNamespace.Tab] = []
    tab: MenuBarNamespace.Tab
    for m in d['data']:
        if 'children' in m:
            tab = MenuBarNamespace.SubmenuTab(
                label=m['text'],
                items=[
                    MenuBarNamespace.SubmenuItem(
                        label=mi['text'],
                        link=mi['url'],
                    )
                    for mi in m['children']
                ],
            )
            tabs.append(tab)
        else:
            tab = MenuBarNamespace.LinkTab(
                label=m['text'],
                link=m['url'],
            )
            tabs.append(tab)

    return BaseMenuBar(
        d=d,
        idt=d['id'],
        kind=d['kind'],
        show_wiki=d['showWiki'],
        tabs=tabs,
    )
