
import os
import asyncio

import redditwarp
#import redditwarp.http.transport.aiohttp
#import aiohttp
from redditwarp.http.transport.ASYNC import get_session_underlying_library_name_and_version

async def main() -> None:
    client = redditwarp.ASYNC.Client(
        os.environ['redditwarp_client_id'],
        os.environ['redditwarp_client_secret'],
        os.environ['redditwarp_refresh_token'],
    )
    async with client:
        client.http.requestor = client.http.authorized_requestor
        print('/'.join(get_session_underlying_library_name_and_version(client.http.session)))
        while True:
            tasks = [asyncio.create_task(client.request('GET', '/api/v1/me')) for _ in range(10)]
            for fut in asyncio.as_completed(tasks):
                await fut
                response = client.last_response
                print({
                    k.removeprefix('x-ratelimit-'): v
                    for k, v in response.headers.items()
                    if k.startswith('x-ratelimit-')
                })

if __name__ == '__main__':
    asyncio.run(main())
