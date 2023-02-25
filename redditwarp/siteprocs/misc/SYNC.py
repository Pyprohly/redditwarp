
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...types import JSON_ro

import json

class MiscProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client

    def convert_richtext_to_markdown(self, rt: Mapping[str, JSON_ro]) -> str:
        """Convert richtext JSON to markdown text."""
        root = self._client.request('POST', '/api/convert_rte_body_format',
                files={'output_mode': 'markdown', 'richtext_json': json.dumps(rt)})
        return root['output']

    def convert_markdown_to_richtext(self, md: str) -> Mapping[str, JSON_ro]:
        """Convert markdown text to richtext JSON."""
        root = self._client.request('POST', '/api/convert_rte_body_format',
                files={'output_mode': 'rtjson', 'markdown_text': md})
        return root['output']
