
from __future__ import annotations
from typing import Mapping, Any

from ..widget_base import (
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
)
from ..widget_SYNC import (
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
from .widget_base import (
    load_base_widget,
    load_base_text_area_widget,
    load_base_button_widget,
    load_base_image_widget,
    load_base_community_list_widget,
    load_base_calendar_widget,
    load_base_post_flair_widget,
    load_base_custom_css_widget,
    load_base_community_details_widget,
    load_base_moderator_list_widget,
    load_base_rules_widget,
    load_base_menu_bar,
)

def load_widget(d: Mapping[str, Any]) -> Widget:
    u = load_base_widget(d)
    if isinstance(u, BaseTextAreaWidget):
        return TextAreaWidget(
            d=u.d,
            idt=u.idt,
            kind=u.kind,
            header_color=u.header_color,
            background_color=u.background_color,
            title=u.title,
            text=u.text,
            text_html=u.text_html,
        )
    if isinstance(u, BaseButtonWidget):
        return ButtonWidget(
            d=u.d,
            idt=u.idt,
            kind=u.kind,
            header_color=u.header_color,
            background_color=u.background_color,
            title=u.title,
            description=u.description,
            description_html=u.description_html,
            buttons=u.buttons,
        )
    if isinstance(u, BaseImageWidget):
        return ImageWidget(
            d=u.d,
            idt=u.idt,
            kind=u.kind,
            header_color=u.header_color,
            background_color=u.background_color,
            title=u.title,
            items=u.items,
        )
    if isinstance(u, BaseCommunityListWidget):
        return CommunityListWidget(
            d=u.d,
            idt=u.idt,
            kind=u.kind,
            header_color=u.header_color,
            background_color=u.background_color,
            title=u.title,
            items=u.items,
        )
    if isinstance(u, BaseCalendarWidget):
        return CalendarWidget(
            d=u.d,
            idt=u.idt,
            kind=u.kind,
            header_color=u.header_color,
            background_color=u.background_color,
            title=u.title,
            google_calendar_id=u.google_calendar_id,
            requires_sync=u.requires_sync,
            configuration=u.configuration,
        )
    if isinstance(u, BasePostFlairWidget):
        return PostFlairWidget(
            d=u.d,
            idt=u.idt,
            kind=u.kind,
            header_color=u.header_color,
            background_color=u.background_color,
            title=u.title,
            display=u.display,
            order=u.order,
            templates=u.templates,
        )
    if isinstance(u, BaseCustomCSSWidget):
        return CustomCSSWidget(
            d=u.d,
            idt=u.idt,
            kind=u.kind,
            header_color=u.header_color,
            background_color=u.background_color,
            title=u.title,
            text=u.text,
            css=u.css,
            height=u.height,
            image_data=u.image_data,
        )
    if isinstance(u, BaseCommunityDetailsWidget):
        return CommunityDetailsWidget(
            d=u.d,
            idt=u.idt,
            kind=u.kind,
            header_color=u.header_color,
            background_color=u.background_color,
            title=u.title,
            public_description=u.public_description,
            subscriber_text=u.subscriber_text,
            viewing_text=u.viewing_text,
            subscriber_count=u.subscriber_count,
            viewing_count=u.viewing_count,
        )
    if isinstance(u, BaseModeratorListWidget):
        return ModeratorListWidget(
            d=u.d,
            idt=u.idt,
            kind=u.kind,
            header_color=u.header_color,
            background_color=u.background_color,
            title=u.title,
            mod_num=u.mod_num,
            mods=u.mods,
        )
    if isinstance(u, BaseRulesWidget):
        return RulesWidget(
            d=u.d,
            idt=u.idt,
            kind=u.kind,
            header_color=u.header_color,
            background_color=u.background_color,
            title=u.title,
            display=u.display,
            rules=u.rules,
        )

    raise Exception


def load_text_area_widget(d: Mapping[str, Any]) -> TextAreaWidget:
    u = load_base_text_area_widget(d)
    return TextAreaWidget(
        d=u.d,
        idt=u.idt,
        kind=u.kind,
        header_color=u.header_color,
        background_color=u.background_color,
        title=u.title,
        text=u.text,
        text_html=u.text_html,
    )

def load_button_widget(d: Mapping[str, Any]) -> ButtonWidget:
    u = load_base_button_widget(d)
    return ButtonWidget(
        d=u.d,
        idt=u.idt,
        kind=u.kind,
        header_color=u.header_color,
        background_color=u.background_color,
        title=u.title,
        description=u.description,
        description_html=u.description_html,
        buttons=u.buttons,
    )

def load_image_widget(d: Mapping[str, Any]) -> ImageWidget:
    u = load_base_image_widget(d)
    return ImageWidget(
        d=u.d,
        idt=u.idt,
        kind=u.kind,
        header_color=u.header_color,
        background_color=u.background_color,
        title=u.title,
        items=u.items,
    )

def load_community_list_widget(d: Mapping[str, Any]) -> CommunityListWidget:
    u = load_base_community_list_widget(d)
    return CommunityListWidget(
        d=u.d,
        idt=u.idt,
        kind=u.kind,
        header_color=u.header_color,
        background_color=u.background_color,
        title=u.title,
        items=u.items,
    )

def load_calendar_widget(d: Mapping[str, Any]) -> CalendarWidget:
    u = load_base_calendar_widget(d)
    return CalendarWidget(
        d=u.d,
        idt=u.idt,
        kind=u.kind,
        header_color=u.header_color,
        background_color=u.background_color,
        title=u.title,
        google_calendar_id=u.google_calendar_id,
        requires_sync=u.requires_sync,
        configuration=u.configuration,
    )

def load_post_flair_widget(d: Mapping[str, Any]) -> PostFlairWidget:
    u = load_base_post_flair_widget(d)
    return PostFlairWidget(
        d=u.d,
        idt=u.idt,
        kind=u.kind,
        header_color=u.header_color,
        background_color=u.background_color,
        title=u.title,
        display=u.display,
        order=u.order,
        templates=u.templates,
    )

def load_custom_css_widget(d: Mapping[str, Any]) -> CustomCSSWidget:
    u = load_base_custom_css_widget(d)
    return CustomCSSWidget(
        d=u.d,
        idt=u.idt,
        kind=u.kind,
        header_color=u.header_color,
        background_color=u.background_color,
        title=u.title,
        text=u.text,
        css=u.css,
        height=u.height,
        image_data=u.image_data,
    )

def load_community_details_widget(d: Mapping[str, Any]) -> CommunityDetailsWidget:
    u = load_base_community_details_widget(d)
    return CommunityDetailsWidget(
        d=u.d,
        idt=u.idt,
        kind=u.kind,
        header_color=u.header_color,
        background_color=u.background_color,
        title=u.title,
        public_description=u.public_description,
        subscriber_text=u.subscriber_text,
        viewing_text=u.viewing_text,
        subscriber_count=u.subscriber_count,
        viewing_count=u.viewing_count,
    )

def load_moderator_list_widget(d: Mapping[str, Any]) -> ModeratorListWidget:
    u = load_base_moderator_list_widget(d)
    return ModeratorListWidget(
        d=u.d,
        idt=u.idt,
        kind=u.kind,
        header_color=u.header_color,
        background_color=u.background_color,
        title=u.title,
        mod_num=u.mod_num,
        mods=u.mods,
    )

def load_rules_widget(d: Mapping[str, Any]) -> RulesWidget:
    u = load_base_rules_widget(d)
    return RulesWidget(
        d=u.d,
        idt=u.idt,
        kind=u.kind,
        header_color=u.header_color,
        background_color=u.background_color,
        title=u.title,
        display=u.display,
        rules=u.rules,
    )


def load_menu_bar(d: Mapping[str, Any]) -> MenuBar:
    u = load_base_menu_bar(d)
    return MenuBar(
        d=u.d,
        idt=u.idt,
        kind=u.kind,
        show_wiki=u.show_wiki,
        tabs=u.tabs,
    )
