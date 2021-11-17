
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterator, overload, Union
if TYPE_CHECKING:
    from .menu_bar_SYNC import MenuBar
    from .community_details_SYNC import CommunityDetailsWidget
    from .moderator_list_SYNC import ModeratorListWidget
    from .rules_SYNC import RulesWidget

from .widget_SYNC import Widget

class WidgetList(Sequence[Widget]):
    def __init__(self,
        *,
        widgets: Sequence[Widget],
        menu_bar: Optional[MenuBar],
        community_details_widget: CommunityDetailsWidget,
        moderator_list_widget: ModeratorListWidget,
        rules_widget: Optional[RulesWidget],
    ) -> None:
        self._widgets = widgets
        self.menu_bar: Optional[MenuBar] = menu_bar
        self._community_details_widget = community_details_widget
        self._moderator_list_widget = moderator_list_widget
        self._rules_widget = rules_widget

    def __len__(self) -> int:
        return len(self._widgets)

    def __contains__(self, item: object) -> bool:
        return item in self._widgets

    def __iter__(self) -> Iterator[Widget]:
        return iter(self._widgets)

    @overload
    def __getitem__(self, index: int) -> Widget: ...
    @overload
    def __getitem__(self, index: slice) -> Sequence[Widget]: ...
    def __getitem__(self, index: Union[int, slice]) -> Union[Widget, Sequence[Widget]]:
        return self._widgets[index]

    def get_community_details_widget(self) -> CommunityDetailsWidget:
        return self._community_details_widget

    def get_moderator_list_widget(self) -> ModeratorListWidget:
        return self._moderator_list_widget

    def get_rules_widget(self) -> Optional[RulesWidget]:
        return self._rules_widget
