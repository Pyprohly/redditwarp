
from dataclasses import dataclass
from types import ModuleType

@dataclass
class TransporterInfo:
    name: str
    version: str
    module: ModuleType

blank_transporter = TransporterInfo('', '', ModuleType(''))
