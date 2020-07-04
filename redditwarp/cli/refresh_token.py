#!/usr/bin/env python3
"""Step through the Authorization Code flow to obtain a refresh token.

If you ever accidentally expose your refresh token or access token,
run this tool to completion to fetch new tokens and the old tokens
will expire and you will be safe.
"""

from __future__ import annotations
from typing import Optional, Mapping

import os
import re
import argparse
import uuid
import socket
import urllib.parse
import webbrowser

import redditwarp

def get_client_cred_input(prompt: str, env: str, x: Optional[str]) -> str:
    print(prompt, end='')
    if x is None:
        x = input()
    if x == '.':
        x = os.environ[env]
    print(x)
    return x

def get_client_id(x: Optional[str]) -> str:
    return get_client_cred_input('Client ID: ', 'redditwarp_client_id', x)

def get_client_secret(x: Optional[str]) -> str:
    return get_client_cred_input('Client secret: ', 'redditwarp_client_secret', x)

parser = argparse.ArgumentParser(description=__doc__)
add_arg = parser.add_argument
add_arg('client_id', nargs='?')
add_arg('--client-id', metavar='CLIENT_ID', dest='client_id_opt', help=argparse.SUPPRESS)
add_arg('client_secret', nargs='?')
add_arg('--client-secret', metavar='CLIENT_SECRET', dest='client_secret_opt', help=argparse.SUPPRESS)
add_arg('--scope', default='*')
add_arg('--redirect-uri', default='http://localhost:8080')
add_arg('--duration', choices=('temporary', 'permanent'), default='permanent', help=argparse.SUPPRESS)
add_arg('--no-web-browser', action='store_true')
args = parser.parse_args()

transporter = redditwarp.http.transport.get_default_sync_transporter()
if transporter is None:
    raise ModuleNotFoundError('An HTTP transport library needs to be installed.')
new_session = transporter.module.new_session  # type: ignore[attr-defined]

print("Reddit OAuth2 Authorization Code flow\n")

client_id = get_client_id(args.client_id_opt or args.client_id)
client_secret = get_client_secret(args.client_secret_opt or args.client_secret)
scope: str = args.scope
redirect_uri: str = args.redirect_uri
duration: str = args.duration
no_web_browser: bool = args.no_web_browser
state = str(uuid.uuid4())

print()
print('''Step 1. Build the authorization URL and direct the user to the authorization server.\n''')

params: Mapping[str, str] = {
    'response_type': 'code',
    'client_id': client_id,
    'redirect_uri': redirect_uri,
    'scope': scope,
    'state': state,
    'duration': duration,
}
url = f"{redditwarp.auth.const.AUTHORIZATION_URL}?{urllib.parse.urlencode(params)}"
print(url)
print()
if not no_web_browser:
    webbrowser.open(url)

print('''Step 2. The authorization server responds to the redirect URI. Extract the authorization code.\n''')

with socket.socket() as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 8080))
    server.listen(1)
    client, addr = server.accept()
    print(addr)

with client:
    data = client.recv(8192)
    client.send(b"HTTP/1.1 200 OK\r\n\r\n" + data)

decoded = data.decode().strip()
print(f"@```\n{decoded}\n```@\n")

m = re.match(r"^GET /\?([^ ]*) HTTP", decoded)
if not m:
    raise Exception
query = m[1]
d = urllib.parse.parse_qs(query)
response_uri_params: Mapping[str, str] = {k: v[0] for k, v in d.items()}

response_state = response_uri_params['state']
if response_state != state:
    raise Exception(f'state did not match: {(response_state, state)}')

try:
    code = response_uri_params['code']
except KeyError:
    raise Exception('The user declined authorization.') from None

print('''Step 3. Exchange the authorization code.\n''')

ua = (
    f'RedditWarp/{redditwarp.__version__} '
    f'{transporter.name}/{transporter.version} '
    'redditwarp.cli.refresh_token'
)
session = new_session(headers={'User-Agent': ua})
token_client = redditwarp.auth.TokenObtainmentClient(
    session,
    redditwarp.auth.const.TOKEN_OBTAINMENT_URL,
    redditwarp.auth.ClientCredentials(client_id, client_secret),
    redditwarp.auth.grants.AuthorizationCodeGrant(code, redirect_uri),
)

print('Obtaining tokens from the token server...\n')
token = token_client.fetch_token()
print(f" Access token : {token.access_token}")
print(f"Refresh token : {token.refresh_token}")
