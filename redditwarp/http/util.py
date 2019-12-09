
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .response import Response

import json

def response_json(response: Response) -> Dict[str, Any]:
	if not response.headers['Content-Type'].startswith('application/json'):
		raise ValueError
	text = response.data.decode()
	json_dict = json.loads(text)
	return json_dict
