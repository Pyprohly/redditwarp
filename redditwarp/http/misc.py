
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any
if TYPE_CHECKING:
    from .response import Response

import json

json_decoder = json.JSONDecoder()
json_loads = json_decoder.decode

def json_loads_response(response: Response) -> Dict[str, Any]:
    if 'application/json' not in response.headers.get('Content-Type', ''):
        raise ValueError
    text = response.data.decode()
    return json_loads(text)
