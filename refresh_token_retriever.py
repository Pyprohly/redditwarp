
import os
import re
import socket
import urllib.parse
import webbrowser

from redditwarp.auth.misc import (
	AUTHORIZATION_ENDPOINT,
	TOKEN_ENDPOINT,
	authorization_url,
)

from redditwarp.auth.grants import AuthorizationCodeGrant
from redditwarp.auth.client import TokenClient, ClientCredentials
from redditwarp.http.transport.requests import new_session

client_id = os.environ['redditwarp_client_id']
client_secret = os.environ['redditwarp_client_secret']
scope = '*'
state = '136134345'
redirect_uri = 'http://localhost:8080'

#'''
url = authorization_url(
	AUTHORIZATION_ENDPOINT,
	'code',
	client_id,
	redirect_uri,
	scope,
	state,
	dict(duration='permanent'),
)
print(url)
print()

webbrowser.open(url)

with socket.socket() as server:
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server.bind(('127.0.0.1', 8080))
	server.listen(1)

	client, addr = server.accept()
	print(f"Connection: {addr}")
	with client:
		data = client.recv(1024)
		client.send(b"HTTP/1.1 200 OK\r\n\r\n" + data)

print(f"Recieved: {data!r}")
print()
m = re.match(r'^GET /\?(.*) HTTP', data.decode())
if not m:
	raise Exception
query = m[1]
response_dict = urllib.parse.parse_qs(query)
response_dict2 = {k: v[0] for k, v in response_dict.items()}

assert response_dict2['state'] == state
'''#'''

code = response_dict2['code'][0]

grant = AuthorizationCodeGrant(code, redirect_uri)
client_credentials = ClientCredentials(client_id, client_secret)
session = new_session(headers={'User-Agent': 'RedditWarp authorization code flow script'})
token_client = TokenClient(session, TOKEN_ENDPOINT, client_credentials, grant)

print('Fetching token...')
print()
token = token_client.fetch_token()

print(f"Refresh Token: {token.refresh_token}")
print(f" Access Token: {token.access_token}")
