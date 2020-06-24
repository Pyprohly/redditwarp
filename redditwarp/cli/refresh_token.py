#!/usr/bin/env python3
"""Retrieve OAuth2 tokens from the Reddit API via the Authorization Code flow."""

from __future__ import annotations
from typing import Optional

import os
import re
import argparse
import uuid
import socket
import urllib.parse
import webbrowser

from redditwarp.http.transport import default_sync_transporter as transporter
from redditwarp import auth

new_session = transporter.module.new_session  # type: ignore[attr-defined]

def get_client_id(x: Optional[str]) -> str:
    print('Client ID: ', end='')
    if x is None:
        x = input()
    if x == '.':
        x = os.environ['redditwarp_client_id']
    print(x)
    return x

def get_client_secret(x: Optional[str]) -> str:
    print('Client secret: ', end='')
    if x is None:
        x = input()
    if x == '.':
        x = os.environ['redditwarp_client_secret']
    print(x)
    return x

parser = argparse.ArgumentParser(description=__doc__)
add_arg = parser.add_argument
add_arg('client_id', nargs='?')
add_arg('--client-id', dest='client_id_opt')
add_arg('client_secret', nargs='?')
add_arg('--client-secret', dest='client_secret_opt')
add_arg('--scopes', default='*')
add_arg('--redirect-uri', default='http://localhost:8080')
add_arg('--duration', choices=('temporary', 'permanent'), default='permanent')
add_arg('--no-web-browser', action='store_true')
args = parser.parse_args()

print('Reddit OAuth2 Authorization Code flow\n')

client_id: str = get_client_id(args.client_id_opt or args.client_id)
client_secret: str = get_client_secret(args.client_secret_opt or args.client_secret)
scopes: str = args.scopes
redirect_uri: str = args.redirect_uri
duration: str = args.duration
no_web_browser: bool = args.no_web_browser
state = str(uuid.uuid4())

print("\nStep 1. Build the authorization URL and direct the user to the authorization server.")

params = {
    'response_type': 'code',
    'client_id': client_id,
    'redirect_uri': redirect_uri,
    'scope': scopes,
    'state': state,
    'duration': duration,
}
url = f'{auth.const.AUTHORIZATION_URL}?{urllib.parse.urlencode(params)}'

print(url)
print()

if not no_web_browser:
    webbrowser.open(url)

print("Step 2. The authorization server sends a response to the redirect URI.")

with socket.socket() as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 8080))
    server.listen(1)
    client, addr = server.accept()
print(f"Connection: {addr}")
with client:
    data = client.recv(8192)
    client.send(b"HTTP/1.1 200 OK\r\n\r\n" + data)

print(f"Recieved: \\\n{data!r}\n")
decoded = data.decode()
print(f"@```\n{decoded}\n```@\n")

m = re.match(r"^GET /\?([^ ]*) HTTP", data.decode())
if not m:
    raise Exception
query = m[1]
d = urllib.parse.parse_qs(query)
response_uri_params = {k: v[0] for k, v in d.items()}

response_state: str = response_uri_params['state']
if response_state != state:
    raise Exception('state did not match: ' + response_state)

try:
    code: str = response_uri_params['code']
except KeyError:
    raise Exception('The user declined authorization.') from None

print("Step 3. Exchange the authorization code.")

session = new_session(headers={'User-Agent': 'RedditWarp redditwarp.cli.refresh_token'})
token_client = auth.TokenObtainmentClient(
    session,
    auth.const.TOKEN_OBTAINMENT_URL,
    auth.ClientCredentials(client_id, client_secret),
    auth.grants.AuthorizationCodeGrant(code, redirect_uri),
)

print('Exchanging the authorization code for a token...', end='')
token = token_client.fetch_token()
print(' Done.')
print()
print(f"Refresh token : {token.refresh_token}")
print(f" Access token : {token.access_token}")
