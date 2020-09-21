
import os
import asyncio

import redditwarp

async def main():
    client = redditwarp.ClientAsync(
        os.environ['redditwarp_client_id'],
        os.environ['redditwarp_client_secret'],
        os.environ['redditwarp_refresh_token'],
    )
    while True:
        tasks = [asyncio.create_task(client.request('GET', '/api/v1/me')) for _ in range(10)]
        for fut in asyncio.as_completed(tasks):
            response = await fut
            print({k[len('x-ratelimit-'):]: v for k, v in response.headers.items() if k.startswith('x-ratelimit')})

    await client.close()

if __name__ == '__main__':
    asyncio.run(main())
