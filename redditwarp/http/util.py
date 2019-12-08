
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .response import Response

import json

def json_from_response(response: Response) -> Dict[str, Any]:
	if 'application/json' not in response.headers['Content-Type']:
		raise ValueError
	text = response.data.decode()
	json_dict = json.loads(text)
	return json_dict
