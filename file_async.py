
import asyncio
from pprint import pprint

import redditwarp

async def main():
	client = redditwarp.ClientAsync('GdfdxbF8ea73oQ', 'sOkVUjcTWNMZY11vWzlMAy4J7UE', username='Pyprohly', password='A2CVdajf2'
	)
	#response = client.request('GET', '/api/info', params={'id': 't1_d98khom'})
	response = await client.request('GET', '/api/v1/me')
	pprint(response.data)
	await client.close()

if __name__ == '__main__':
	asyncio.run(main())
