
import collections

from . import requests
from . import aiohttp

TransportInfo = collections.namedtuple('TransportInfo', 'name version_string session')

transport_reg = {
	'requests': TransportInfo('requests', requests.version_string, requests.Session),
	'aiohttp': TransportInfo('aiohttp', aiohttp.version_string, aiohttp.Session),
}
