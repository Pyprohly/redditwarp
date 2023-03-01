
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable
if TYPE_CHECKING:
    from ..response import Response

import json

json_decoder: json.JSONDecoder = json.JSONDecoder()
json_decode: Callable[[str], Any] = json_decoder.decode

def load_json_from_response(resp: Response, /) -> Any:
    """Return the JSON data contained in a response object.

    .. .PARAMETERS

    :param response:
    :type response: :class:`~.http.response.Response`

    .. .RETURNS

    :rtype: `Any`

    .. .RAISES

    :raises ValueError:
        The response does not contain valid JSON data.
    """
    return json_decode(resp.data.decode())

def load_json_from_response_but_prefer_status_code_exception_on_failure(resp: Response, /) -> Any:
    """Return the JSON data contained in a response object.

    Behaves similarly to :func:`.load_json_from_response` but prefers to raise a
    :class:`~redditwarp.http.exceptions.StatusCodeException`
    instead of a `ValueError` when the response body does not contain JSON.
    """
    try:
        return load_json_from_response(resp)
    except ValueError as cause:
        try:
            resp.ensure_successful_status()
        except Exception as exc:
            raise exc from cause
        raise
