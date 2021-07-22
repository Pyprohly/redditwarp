
from __future__ import annotations
from typing import Optional, Mapping

import urllib.parse

NO_VALUE_PARAM_PLACEHOLDER = 'd07d4b7d-d881-4217-9bca-42ed0c6a3d04'

def join_params(uri: str, params: Mapping[str, Optional[str]]) -> str:
    url_parts = list(urllib.parse.urlparse(uri))
    query_dict = urllib.parse.parse_qs(url_parts[4])

    none_value_keys = []
    for k, v in params.items():
        if v is None:
            none_value_keys.append(k)
            v = NO_VALUE_PARAM_PLACEHOLDER
        query_dict.setdefault(k, []).append(v)

    params_str = urllib.parse.urlencode(query_dict, doseq=True)

    for k in none_value_keys:
        params_str = params_str.replace(f'{k}={NO_VALUE_PARAM_PLACEHOLDER}', k)

    url_parts[4] = params_str
    return urllib.parse.urlunparse(url_parts)
