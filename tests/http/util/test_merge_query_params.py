
from redditwarp.http.util.merge_query_params import merge_query_params

def test_merge_query_params() -> None:
    url = 'http://example.com/asdf'
    url2 = 'http://example.com/asdf?z=26'
    assert merge_query_params(url, {'a': '1', 'b': None, 'c': ''}) == f'{url}?a=1&b&c='
    assert merge_query_params(url, {'a': None, 'b': '', 'c': '1'}) == f'{url}?a&b=&c=1'
    assert merge_query_params(url, {'a': '', 'b': '1', 'c': None}) == f'{url}?a=&b=1&c'
    assert merge_query_params(url2, {'a': '1'}) == f'{url2}&a=1'
