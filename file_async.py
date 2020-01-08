
import asyncio
from pprint import pprint

import redditwarp

async def main():
	async with (
		redditwarp.ClientAsync('GdfdxbF8ea73oQ', 'sOkVUjcTWNMZY11vWzlMAy4J7UE', username='Pyprohly', password='A2CVdajf2')
	) as client:
		'''
		response = await client.request('GET', '/api/v1/me')
		pprint(response.data)
		'''
		data = await client.request_json('GET', '/api/v1/me')
		pprint(data)

	globals().update(locals())

if __name__ == '__main__':
	asyncio.run(main())
