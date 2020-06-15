
from typing import Any
from dataclasses import dataclass

from . import requests
from . import aiohttp

@dataclass
class _TransportInfo:
    name: str
    version_string: str
    session: Any

transport_reg = {
    'requests': _TransportInfo('requests', requests.version_string, requests.Session),
    'aiohttp': _TransportInfo('aiohttp', aiohttp.version_string, aiohttp.Session),
}
