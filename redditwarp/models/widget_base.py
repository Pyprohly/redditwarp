
from __future__ import annotations
from typing import Mapping, Any, Optional, Sequence, TypeVar, Generic, Iterator, overload, Union

from dataclasses import dataclass

from .artifact import IArtifact
from .widget import (
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

@dataclass(repr=False, eq=False)
class BaseWidget(IArtifact):
    d: Mapping[str, Any]
    idt: str
    kind: str
    header_color: str
    background_color: str
    title: str

@dataclass(repr=False, eq=False)
class BaseTextAreaWidget(BaseWidget):
    text: str
    text_html: str

@dataclass(repr=False, eq=False)
class BaseButtonWidget(BaseWidget):
    description: str
    description_html: str
    buttons: Sequence[ButtonWidgetNamespace.Button]

@dataclass(repr=False, eq=False)
class BaseImageWidget(BaseWidget):
    items: Sequence[ImageWidgetNamespace.ImageWidgetItem]

@dataclass(repr=False, eq=False)
class BaseCommunityListWidget(BaseWidget):
    items: Sequence[CommunityListWidgetNamespace.CommunityListWidgetItem]

@dataclass(repr=False, eq=False)
class BaseCalendarWidget(BaseWidget):
    google_calendar_id: str
    requires_sync: bool
    configuration: CalendarWidgetNamespace.CalendarWidgetConfiguration

@dataclass(repr=False, eq=False)
class BasePostFlairWidget(BaseWidget):
    display: str
    order: Sequence[str]
    templates: Sequence[PostFlairWidgetNamespace.PostFlairWidgetItem]

@dataclass(repr=False, eq=False)
class BaseCustomCSSWidget(BaseWidget):
    text: str
    css: str
    height: Optional[int]
    image_data: Sequence[CustomCSSWidgetNamespace.CustomCSSWidgetImageInfo]

@dataclass(repr=False, eq=False)
class BaseCommunityDetailsWidget(BaseWidget):
    public_description: str
    subscriber_text: str
    viewing_text: str
    subscriber_count: int
    viewing_count: int

@dataclass(repr=False, eq=False)
class BaseModeratorListWidget(BaseWidget):
    mod_num: int
    mods: Sequence[ModeratorListWidgetNamespace.ModeratorInfo]

@dataclass(repr=False, eq=False)
class BaseRulesWidget(BaseWidget):
    display: str
    rules: Sequence[RulesWidgetNamespace.Rule]


@dataclass(repr=False, eq=False)
class BaseMenuBar:
    d: Mapping[str, Any]
    idt: str
    kind: str
    show_wiki: bool
    tabs: Sequence[MenuBarNamespace.Tab]


TWidget = TypeVar('TWidget', bound=BaseWidget)
TMenuBar = TypeVar('TMenuBar', bound=BaseMenuBar)
TCommunityDetailsWidget = TypeVar('TCommunityDetailsWidget', bound=BaseCommunityDetailsWidget)
TModeratorListWidget = TypeVar('TModeratorListWidget', bound=BaseModeratorListWidget)
TRulesWidget = TypeVar('TRulesWidget', bound=BaseRulesWidget)

class GenericBaseWidgetList(
    Sequence[TWidget],
    Generic[
        TWidget,
        TMenuBar,
        TCommunityDetailsWidget,
        TModeratorListWidget,
        TRulesWidget,
    ],
):
    def __init__(self,
        *,
        widgets: Sequence[TWidget],
        menu_bar: Optional[TMenuBar],
        community_details_widget: TCommunityDetailsWidget,
        moderator_list_widget: TModeratorListWidget,
        rules_widget: Optional[TRulesWidget],
    ) -> None:
        self._widgets = widgets
        self.menu_bar: Optional[TMenuBar] = menu_bar
        self._community_details_widget = community_details_widget
        self._moderator_list_widget = moderator_list_widget
        self._rules_widget = rules_widget

    def __len__(self) -> int:
        return len(self._widgets)

    def __contains__(self, item: object) -> bool:
        return item in self._widgets

    def __iter__(self) -> Iterator[TWidget]:
        return iter(self._widgets)

    @overload
    def __getitem__(self, index: int) -> TWidget: ...
    @overload
    def __getitem__(self, index: slice) -> Sequence[TWidget]: ...
    def __getitem__(self, index: Union[int, slice]) -> Union[TWidget, Sequence[TWidget]]:
        return self._widgets[index]

    def get_community_details_widget(self) -> TCommunityDetailsWidget:
        return self._community_details_widget

    def get_moderator_list_widget(self) -> TModeratorListWidget:
        return self._moderator_list_widget

    def get_rules_widget(self) -> Optional[TRulesWidget]:
        return self._rules_widget
