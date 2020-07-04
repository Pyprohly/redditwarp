
import os
from pprint import pprint

import redditwarp

def main():
	try:
		client = redditwarp.Client(
			os.environ['redditwarp_client_id'],
			os.environ['redditwarp_client_secret'],
			os.environ['redditwarp_refresh_token'],
		)
		client.set_user_agent("u_Pyprohly/v0 (by u/Pyprohly)")
		print(client.http.user_agent)
		with client:
			data = client.request('GET', '/api/v1/me')
			pprint(data)

	except Exception:
		print(client.last_response.data.decode())
	finally:
		globals().update(locals())

if __name__ == '__main__':
	main()
