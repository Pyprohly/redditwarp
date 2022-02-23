
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ...client_SYNC import Client

import json

class MiscProcedures:
    def __init__(self, client: Client):
        self._client = client

    def convert_rtjson_to_markdown(self, rtjson: Mapping[str, Any]) -> str:
        root = self._client.request('POST', '/api/convert_rte_body_format',
                data={'output_mode': 'markdown', 'richtext_json': json.dumps(rtjson)})
        return root['output']

    def convert_markdown_to_rtjson(self, md: str) -> Mapping[str, Any]:
        root = self._client.request('POST', '/api/convert_rte_body_format',
                data={'output_mode': 'rtjson', 'markdown_text': md})
        return root['output']
