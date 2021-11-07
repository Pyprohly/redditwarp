
from __future__ import annotations

from dataclasses import dataclass

from .widget_base import (
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
    GenericBaseWidgetList,
)

@dataclass(repr=False, eq=False)
class Widget(BaseWidget):
    pass

@dataclass(repr=False, eq=False)
class TextAreaWidget(Widget, BaseTextAreaWidget):
    pass

@dataclass(repr=False, eq=False)
class ButtonWidget(Widget, BaseButtonWidget):
    pass

@dataclass(repr=False, eq=False)
class ImageWidget(Widget, BaseImageWidget):
    pass

@dataclass(repr=False, eq=False)
class CommunityListWidget(Widget, BaseCommunityListWidget):
    pass

@dataclass(repr=False, eq=False)
class CalendarWidget(Widget, BaseCalendarWidget):
    pass

@dataclass(repr=False, eq=False)
class PostFlairWidget(Widget, BasePostFlairWidget):
    pass

@dataclass(repr=False, eq=False)
class CustomCSSWidget(Widget, BaseCustomCSSWidget):
    pass

@dataclass(repr=False, eq=False)
class CommunityDetailsWidget(Widget, BaseCommunityDetailsWidget):
    pass

@dataclass(repr=False, eq=False)
class ModeratorListWidget(Widget, BaseModeratorListWidget):
    pass

@dataclass(repr=False, eq=False)
class RulesWidget(Widget, BaseRulesWidget):
    pass


@dataclass(repr=False, eq=False)
class MenuBar(BaseMenuBar):
    pass


class WidgetList(
    GenericBaseWidgetList[
        Widget,
        MenuBar,
        CommunityDetailsWidget,
        ModeratorListWidget,
        RulesWidget,
    ],
): pass
