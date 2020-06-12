
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..client_sync import Client

from .fetch.fetch_sync import fetch

class SiteProcedures:
	def __init__(self, client: Client):
		self._client = client
		self.fetch = fetch(client)
