
import pytest

from redditwarp.http.util.json_loads import json_loads_response
from redditwarp.http.response import Response

def test_json_loads_response():
    resp = Response(200, {'Content-Type': 'application/json'}, b'{"hello": "world"}')
    json_dict = json_loads_response(resp)
    assert json_dict == {"hello": "world"}

def test_json_loads_response__exception():
    resp = Response(200, {}, b'{"hello": "world"}')
    with pytest.raises(ValueError):
        json_loads_response(resp)
