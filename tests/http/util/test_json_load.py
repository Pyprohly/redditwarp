
import pytest

from redditwarp.http.util.json_loading import load_json_from_response
from redditwarp.http.response import Response

def test_load_json_from_response() -> None:
    resp = Response(200, {'Content-Type': 'application/json'}, b'{"hello": "world"}')
    json_dict = load_json_from_response(resp)
    assert json_dict == {"hello": "world"}

def test_load_json_from_response__exception() -> None:
    resp = Response(200, {}, b'{"hello": "world"}')
    with pytest.raises(ValueError):
        load_json_from_response(resp)
