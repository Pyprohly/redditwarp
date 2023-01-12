
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...types import JSON_ro

import json

class MiscProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client

    def convert_richtext_to_markdown(self, rtjson: Mapping[str, JSON_ro]) -> str:
        root = self._client.request('POST', '/api/convert_rte_body_format',
                files={'output_mode': 'markdown', 'richtext_json': json.dumps(rtjson)})
        return root['output']

    def convert_markdown_to_richtext(self, md: str) -> Mapping[str, JSON_ro]:
        root = self._client.request('POST', '/api/convert_rte_body_format',
                files={'output_mode': 'rtjson', 'markdown_text': md})
        return root['output']
