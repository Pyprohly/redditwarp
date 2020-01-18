
import asyncio

import redditwarp

async def main():
	client = redditwarp.ClientAsync('GdfdxbF8ea73oQ', 'sOkVUjcTWNMZY11vWzlMAy4J7UE', username='Pyprohly', password='A2CVdajf2')
	while True:
		tasks = [asyncio.create_task(client.request('GET', '/api/v1/me')) for _ in range(10)]
		for fut in asyncio.as_completed(tasks):
			response = await fut
			print({k[len('x-ratelimit-'):]: v for k, v in response.headers.items() if k.startswith('x-ratelimit')})

	await client.close()

if __name__ == '__main__':
	asyncio.run(main())
