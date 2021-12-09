
from __future__ import annotations
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from ..http.response import Response

from ..http.util.json_load import json_loads_response
from ..exceptions import raise_for_non_json_response

def json_loads_reddit_response(response: Response) -> Any:
    try:
        json_data = json_loads_response(response)
    except ValueError as cause:
        try:
            raise_for_non_json_response(response)
        except Exception as exc:
            raise exc from cause
        raise
    return json_data
