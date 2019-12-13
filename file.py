
from pprint import pprint

import redditwarp
from redditwarp.http.transport.requests import Session
from redditwarp.http.request import Request

#client = redditwarp.Client('GdfdxbF8ea73oQ', 'sOkVUjcTWNMZY11vWzlMAy4J7UE', username='Pyprohly', password='A2CVdajf2')

#response = client.request('GET', '/api/info', params={'id': 't1_d98khom'})

session = Session()
#session.headers['User-Agent'] = 'RedditWarp token retrieve script'
session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
session.session.verify = False

params = {
	'client_id': 'GdfdxbF8ea73oQ',
	'redirect_uri': 'http://localhost:8080',
	'scope': '*',
	'state': '136134345',
	'response_type': 'code',
	'duration': 'temporary',
	#'uh': '8fwrw5uzov9fec0431c403ead6dd8a6b551d209c6d817e768c',
	#'authorize': 'Allow',
}

r = Request('GET', 'https://www.google.com')
response = session.request(r)

pprint(response.data)
