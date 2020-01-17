
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any
if TYPE_CHECKING:
	from .response import Response

import json

def response_json(response: Response) -> Dict[str, Any]:
	if not response.headers.get('Content-Type', '').startswith('application/json'):
		raise ValueError
	text = response.data.decode()
	return json.loads(text)
