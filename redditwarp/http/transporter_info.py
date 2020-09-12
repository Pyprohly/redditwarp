
from __future__ import annotations

from dataclasses import dataclass
from importlib.machinery import ModuleSpec

@dataclass
class TransporterInfo:
    name: str
    version: str
    spec: ModuleSpec

blank_transporter = TransporterInfo('', '', ModuleSpec('', None))
