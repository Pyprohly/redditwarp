
from typing import TYPE_CHECKING, Any, Optional, Mapping
if TYPE_CHECKING:
	from ...models.submission import Submission

from ...models.submission import TextPost, LinkPost

def load_submission(d: Mapping[str, Any]) -> Submission:
	data = d['data']
	is_self = data['is_self']
	if is_self:
		TextPost(data)
	return LinkPost(data)

def try_load_linkpost(d: Mapping[str, Any]) -> Optional[LinkPost]:
	data = d['data']
	is_self = data['is_self']
	if is_self:
		return None
	return LinkPost(data)

def try_load_textpost(d: Mapping[str, Any]) -> Optional[TextPost]:
	data = d['data']
	is_self = data['is_self']
	if is_self:
		TextPost(data)
	return None
