
import collections

from . import requests
from . import aiohttp

Transport = collections.namedtuple('Transport', 'name version_string session')

transport_reg = {
	'requests': Transport('requests', requests.version_string, requests.Session),
	'aiohttp': Transport('aiohttp', aiohttp.version_string, aiohttp.Session),
}
