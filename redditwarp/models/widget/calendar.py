
from __future__ import annotations

from dataclasses import dataclass

@dataclass(repr=False, eq=False)
class CalendarWidgetConfiguration:
    num_events: int
    show_title: bool
    show_description: bool
    show_location: bool
    show_date: bool
    show_time: bool
