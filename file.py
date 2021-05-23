
import os
from pprint import pprint

import redditwarp

def main() -> None:
    client = redditwarp.SYNC.Client(
        os.environ['redditwarp_client_id'],
        os.environ['redditwarp_client_secret'],
        os.environ['redditwarp_refresh_token'],
    )
    try:
        client.set_user_agent("u_Pyprohly/v0 (by u/Pyprohly)")
        print(client.http.user_agent)
        with client:
            data = client.request('GET', '/api/v1/me')
            pprint(data)

    except Exception:
        last_resp = client.last_response
        if last_resp is not None:
            print(last_resp.data.decode())
    finally:
        globals().update(locals())

if __name__ == '__main__':
    main()
