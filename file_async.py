
import os
import asyncio
from pprint import pprint

import redditwarp

async def main():
	client = redditwarp.ClientAsync(
		os.environ['redditwarp_client_id'],
		os.environ['redditwarp_client_secret'],
		os.environ['redditwarp_refresh_token'],
	)
	print(client.http.user_agent)
	async with client:
		#'''
		response = await client.request('GET', '/api/v1/me')
		pprint(response.data)
		'''
		data = await client.request_json('GET', '/api/v1/me')
		pprint(data)
		'''#'''

	globals().update(locals())

if __name__ == '__main__':
	asyncio.run(main())
