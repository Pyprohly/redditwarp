
from redditwarp.http.util.join_params_ import join_params

uri = 'http://example.com/asdf'

def test_join_params() -> None:
    assert join_params(uri, {'a': '1', 'b': None, 'c': ''}) == f'{uri}?a=1&b&c='
    assert join_params(uri, {'a': None, 'b': '', 'c': '1'}) == f'{uri}?a&b=&c=1'
    assert join_params(uri, {'a': '', 'b': '1', 'c': None}) == f'{uri}?a=&b=1&c'
