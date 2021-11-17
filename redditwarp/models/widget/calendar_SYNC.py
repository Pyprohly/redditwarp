
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .calendar import CalendarWidgetConfiguration

from dataclasses import dataclass

from .widget_SYNC import Widget

@dataclass(repr=False, eq=False)
class CalendarWidget(Widget):
    google_calendar_id: str
    requires_sync: bool
    configuration: CalendarWidgetConfiguration
