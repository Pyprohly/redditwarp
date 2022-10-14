
from __future__ import annotations
from typing import Optional, Mapping

import urllib.parse

_NO_VALUE_PARAM_PLACEHOLDER = 'NO_VALUE_PARAM_PLACEHOLDER__d07d4b7d-d881-4217-9bca-42ed0c6a3d04'

def merge_query_params(uri: str, params: Mapping[str, Optional[str]]) -> str:
    """Merge and return `uri` with `params`.

    The mapping values for `params` can be `None`. A `None` value indicates that the
    equals delimiter symbol should be omitted.
    """
    urlparts = list(urllib.parse.urlparse(uri))
    query_dict = urllib.parse.parse_qs(urlparts[4])

    none_keys = []
    for k, v in params.items():
        if v is None:
            none_keys.append(k)
            v = _NO_VALUE_PARAM_PLACEHOLDER
        query_dict.setdefault(k, []).append(v)

    query = urllib.parse.urlencode(query_dict, doseq=True)

    for k in none_keys:
        query = query.replace(f'{k}={_NO_VALUE_PARAM_PLACEHOLDER}', k)

    urlparts[4] = query
    return urllib.parse.urlunparse(urlparts)
