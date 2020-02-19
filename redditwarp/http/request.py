
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Optional
	from collections.abc import Mapping
	from .payload import Payload

from dataclasses import dataclass, field

@dataclass
class Request:
	r"""An data class that stores information about an outgoing request.

	Attributes
	----------
	verb: str
		The HTTP method to use for the request.
	url: str
		The URL to be requested.
	params: Mapping[str, str]
		Query parameters appended to the URL.
	payload: Optional[:class:`.Payload`]
		The payload/body of the HTTP request.
	headers: Mapping[str, str]
		Request headers.
	"""

	verb: str
	url: str
	params: Mapping[str, str] = field(default_factory=dict)
	payload: Optional[Payload] = None
	headers: Mapping[str, str] = field(default_factory=dict)
