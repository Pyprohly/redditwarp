
import time
from pprint import pprint
import redditwarp

start_time = time.time()

client = redditwarp.Client('GdfdxbF8ea73oQ', 'sOkVUjcTWNMZY11vWzlMAy4J7UE', username='Pyprohly', password='A2CVdajf2',
)

#response = client.request('GET', '/api/info', params={'id': 't1_d98khom'})

params = {
	'client_id': 'GdfdxbF8ea73oQ',
	'redirect_uri': 'http://localhost:8080',
	'scope': '*',
	'state': '136134345',
	'response_type': 'code',
	'duration': 'temporary',
	'uh': '8fwrw5uzov9fec0431c403ead6dd8a6b551d209c6d817e768c',
	'authorize': 'Allow',
}
response = client.request('POST', '/api/v1/authorize', params=params)

pprint(response.data)
