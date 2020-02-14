
import os
from pprint import pprint

import redditwarp

def main():
	client = redditwarp.Client(
		os.environ['redditwarp_client_id'],
		os.environ['redditwarp_client_secret'],
		os.environ['redditwarp_refresh_token'],
	)
	print(client.http.user_agent)
	with client:
		'''
		response = client.http.request('GET', '/api/v1/me')
		pprint(response.data)
		'''
		data = client.request('GET', '/api/v1/me')
		pprint(data)
		'''#'''

	globals().update(locals())

if __name__ == '__main__':
	main()
