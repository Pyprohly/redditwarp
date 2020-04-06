
import sys  # noqa
import os
from pprint import pprint  # noqa

import redditwarp

def main():
	try:
		client = redditwarp.Client(
			os.environ['redditwarp_client_id'],
			os.environ['redditwarp_client_secret'],
			os.environ['redditwarp_refresh_token'],
		)
		#client.http.user_agent = 'Mozilla/5.0 (compatible; Charlotte/1.1; http://www.searchme.com/support/)'
		#client.http.user_agent = 'console:myapp:v0 by /u/Pyprohly'
		#client.http.user_agent = 'PyprohlyBot by /u/Pyprohly PRAW/6.5.1 prawcore/1.0.1'
		print(client.http.user_agent)
		with client:
			'''
			response = client.http.request('POST', '/api/lock')
			pprint(response.status)
			pprint(response.data)
			'''
			data = client.request('GET', '/api/v1/me')
			pprint(data)
			'''#'''

	finally:
		globals().update(locals())

if __name__ == '__main__':
	main()
