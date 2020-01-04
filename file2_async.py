
import asyncio
from pprint import pprint

import redditwarp

async def main():
	client = redditwarp.ClientAsync('GdfdxbF8ea73oQ', 'sOkVUjcTWNMZY11vWzlMAy4J7UE', username='Pyprohly', password='A2CVdajf2'
	)
	while True:
		tasks = [client.request('GET', '/api/v1/me') for _ in range(10)]
		responses = await asyncio.gather(*tasks)
		for response in responses:
			print({k: v for k, v in response.headers.items() if k.startswith('x-ratelimit')})

	await client.close()

if __name__ == '__main__':
	asyncio.run(main())
