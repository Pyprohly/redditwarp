
from __future__ import annotations
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from ..response import Response

import json

json_decoder = json.JSONDecoder()
json_decode = json_decoder.decode

def json_loads_response(response: Response) -> Any:
    if not response.headers.get('Content-Type', '').startswith('application/json'):
        raise ValueError
    text = response.data.decode()
    return json_decode(text)
