
import re
import socket
import urllib.parse
from pprint import pprint

import redditwarp
from redditwarp.auth.helper import (
	AUTHORIZATION_ENDPOINT,
	TOKEN_ENDPOINT,
	authorization_url,
)

from redditwarp.auth.grant import AuthorizationCodeGrant
from redditwarp.auth.credentials import ClientCredentials
from redditwarp.http.transport.requests import Session
from redditwarp.auth.client import TokenClient

#client = redditwarp.Client('GdfdxbF8ea73oQ', 'sOkVUjcTWNMZY11vWzlMAy4J7UE', username='Pyprohly', password='A2CVdajf2')

#response = client.request('GET', '/api/info', params={'id': 't1_d98khom'})

state = '136134345'
redirect_uri = 'http://localhost:8080'

url = authorization_url(
	AUTHORIZATION_ENDPOINT,
	'code',
	'GdfdxbF8ea73oQ',
	redirect_uri,
	'*',
	state,
)

print(url)

with socket.socket() as server:
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server.bind(('127.0.0.1', 8080))
	server.listen(1)

	client, addr = server.accept()
	print(f"Connection: {addr}")
	with client:
		data = client.recv(1024)
		client.send(b"HTTP/1.1 200 OK\r\n\r\n" + data)

print(f"Recieved: {data}")
query = re.match(r'^GET /\?(.*) HTTP', data.decode())[1]
response_dict = urllib.parse.parse_qs(query)
response_dict = {k: v[0] for k, v in response_dict.items()}

assert response_dict['state'] == state

grant = AuthorizationCodeGrant(
	response_dict['code'],
	redirect_uri,
)

client_credentials = ClientCredentials('GdfdxbF8ea73oQ', 'sOkVUjcTWNMZY11vWzlMAy4J7UE')

session = Session()
session.headers['User-Agent'] = 'RedditWarp authorization code flow script'
token_client = TokenClient(
	session,
	TOKEN_ENDPOINT,
	client_credentials,
	grant,
)

token = token_client.fetch_token()
