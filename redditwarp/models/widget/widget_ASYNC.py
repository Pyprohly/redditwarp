
from __future__ import annotations
from typing import Mapping, Any

from dataclasses import dataclass

from ..artifact import IArtifact

@dataclass(repr=False, eq=False)
class Widget(IArtifact):
    d: Mapping[str, Any]
    idt: str
    kind: str
    header_color: str
    background_color: str
    title: str
