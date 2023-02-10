
from __future__ import annotations
from typing import Mapping, Any, Optional

from ..models.widget.ASYNC import (
    Widget,
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
from ..models.widget.image_size_named_tuple import ImageSize
from ..models.widget.image import ImageWidgetItem
from ..models.widget.button import (
    HoverState,
    TextHoverState,
    ImageHoverState,
    Button,
    TextButton,
    ImageButton,
)
from ..models.widget.community_list import CommunityListWidgetItem
from ..models.widget.calendar import CalendarWidgetConfiguration
from ..models.widget.post_flair import PostFlairWidgetItem
from ..models.widget.custom_css import CustomCSSWidgetImageInfo
from ..models.widget.moderator_list import ModeratorInfo
from ..models.widget.rules import Rule
from ..models.widget.menu_bar import Tab, LinkTab, SubmenuItem, SubmenuTab


def load_widget(d: Mapping[str, Any]) -> Widget:
    kind = d['kind']
    if kind == 'textarea':
        return load_text_area_widget(d)
    elif kind == 'button':
        return load_button_widget(d)
    elif kind == 'image':
        return load_image_widget(d)
    elif kind == 'community-list':
        return load_community_list_widget(d)
    elif kind == 'calendar':
        return load_calendar_widget(d)
    elif kind == 'post-flair':
        return load_post_flair_widget(d)
    elif kind == 'custom':
        return load_custom_css_widget(d)
    elif kind == 'id-card':
        return load_community_details_widget(d)
    elif kind == 'moderators':
        return load_moderator_list_widget(d)
    elif kind == 'subreddit-rules':
        return load_rules_widget(d)
    raise Exception

def load_text_area_widget(d: Mapping[str, Any]) -> TextAreaWidget:
    styles = d['styles']
    return TextAreaWidget(
        d=d,
        idt=d['id'],
        kind=d['kind'],
        header_color=styles['headerColor'] or '',
        background_color=styles['backgroundColor'] or '',
        title=d['shortName'],
        text=d['text'],
        text_html=d['textHtml'],
    )

def load_button_widget(d: Mapping[str, Any]) -> ButtonWidget:
    styles = d['styles']
    buttons: list[Button] = []
    for m in d['buttons']:
        hover_state: Optional[HoverState] = None
        hs = m['hoverState']
        if hs is not None:
            if hs['kind'] == 'text':
                hover_state = TextHoverState(
                    label=hs['text'],
                    text_color=hs.get('textColor', ''),
                    fill_color=hs.get('fillColor', ''),
                    stroke_color=hs['color'],
                )
            else:
                hover_state = ImageHoverState(
                    image_url=hs['text'],
                    image_size=ImageSize(hs['width'], hs['height']),
                )

        btn: Button
        if m['kind'] == 'text':
            btn = TextButton(
                label=m['text'],
                link=m['url'],
                hover_state=hover_state,
                text_color=m.get('textColor', ''),
                fill_color=m.get('fillColor', ''),
                stroke_color=m['color'],
            )
            buttons.append(btn)
        else:
            btn = ImageButton(
                label=m['text'],
                link=m['linkUrl'],
                hover_state=hover_state,
                image_url=m['url'],
                image_size=ImageSize(m['width'], m['height']),
            )
            buttons.append(btn)

    return ButtonWidget(
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

def load_image_widget(d: Mapping[str, Any]) -> ImageWidget:
    styles = d['styles']
    image_items = [
        ImageWidgetItem(
            url=m['url'],
            size=ImageSize(m['width'], m['height']),
            link=m['linkUrl'] or '',
        )
        for m in d['data']
    ]
    return ImageWidget(
        d=d,
        idt=d['id'],
        kind=d['kind'],
        header_color=styles['headerColor'] or '',
        background_color=styles['backgroundColor'] or '',
        title=d['shortName'],
        items=image_items,
    )

def load_community_list_widget(d: Mapping[str, Any]) -> CommunityListWidget:
    styles = d['styles']
    subr_items = [
        CommunityListWidgetItem(
            name=m['name'],
            subscribers=m['subscribers'],
            icon_img=m['iconUrl'],
            community_icon=m['communityIcon'],
            primary_color=m['primaryColor'],
            nsfw=m['isNSFW'],
        )
        for m in d['data']
    ]
    return CommunityListWidget(
        d=d,
        idt=d['id'],
        kind=d['kind'],
        header_color=styles['headerColor'] or '',
        background_color=styles['backgroundColor'] or '',
        title=d['shortName'],
        items=subr_items,
    )

def load_calendar_widget(d: Mapping[str, Any]) -> CalendarWidget:
    styles = d['styles']
    m = d['configuration']
    configuration = CalendarWidgetConfiguration(
        num_events=m['numEvents'],
        show_title=m['showTitle'],
        show_description=m['showDescription'],
        show_location=m['showLocation'],
        show_date=m['showDate'],
        show_time=m['showTime'],
    )
    return CalendarWidget(
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

def load_post_flair_widget(d: Mapping[str, Any]) -> PostFlairWidget:
    styles = d['styles']
    templates = [
        PostFlairWidgetItem(
            d=m,
            uuid=m['templateId'],
            text_mode=m['type'],
            text=m['text'],
            bg_color=m['backgroundColor'],
            fg_color_scheme=m['textColor'],
        )
        for m in d['templates']
    ]
    return PostFlairWidget(
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

def load_custom_css_widget(d: Mapping[str, Any]) -> CustomCSSWidget:
    styles = d['styles']
    image_data = [
        CustomCSSWidgetImageInfo(
            url=m['url'],
            width=m['width'],
            height=m['height'],
            name=m['name'],
        )
        for m in d['imageData']
    ]
    return CustomCSSWidget(
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

def load_community_details_widget(d: Mapping[str, Any]) -> CommunityDetailsWidget:
    styles = d['styles']
    return CommunityDetailsWidget(
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

def load_moderator_list_widget(d: Mapping[str, Any]) -> ModeratorListWidget:
    styles = d['styles']
    mods = [
        ModeratorInfo(
            name=m['name'],
            flair=ModeratorInfo.Flair(
                text_mode=m['authorFlairType'],
                text=m['authorFlairText'] or '',
                bg_color=m['authorFlairBackgroundColor'],
                fg_color_scheme=m['authorFlairTextColor'],
                has_had_flair_assigned_before_in_subreddit=m['authorFlairText'] is not None,
            ),
        )
        for m in d.get('mods', ())
    ]
    return ModeratorListWidget(
        d=d,
        idt=d['id'],
        kind=d['kind'],
        header_color=styles['headerColor'] or '',
        background_color=styles['backgroundColor'] or '',
        title='',
        mod_num=d.get('totalMods', 0),
        mods=mods,
    )

def load_rules_widget(d: Mapping[str, Any]) -> RulesWidget:
    styles = d['styles']
    rules = [
        Rule(
            description=m['description'],
            description_html=m['descriptionHtml'],
            short_name=m['shortName'],
            violation_reason=m['violationReason'],
            created_ut=m['createdUtc'],
        )
        for m in d.get('data', ())
    ]
    return RulesWidget(
        d=d,
        idt=d['id'],
        kind=d['kind'],
        header_color=styles['headerColor'] or '',
        background_color=styles['backgroundColor'] or '',
        title=d['shortName'],
        display=d['display'],
        rules=rules,
    )


def load_menu_bar(d: Mapping[str, Any]) -> MenuBar:
    tabs: list[Tab] = []
    tab: Tab
    for m in d['data']:
        if 'children' in m:
            tab = SubmenuTab(
                label=m['text'],
                items=[
                    SubmenuItem(
                        label=mi['text'],
                        link=mi['url'],
                    )
                    for mi in m['children']
                ],
            )
            tabs.append(tab)
        else:
            tab = LinkTab(
                label=m['text'],
                link=m['url'],
            )
            tabs.append(tab)

    return MenuBar(
        d=d,
        idt=d['id'],
        kind=d['kind'],
        show_wiki=d['showWiki'],
        tabs=tabs,
    )
