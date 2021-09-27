#!/usr/bin/env python3
"""
Step through the OAuth2 Authorization Code Flow to obtain OAuth2 tokens.

Visit <https://www.reddit.com/prefs/apps> to create an app for your client.

Your app's redirect URI must *exactly* match `http://localhost:8080`.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from types import FrameType

globalz = globals()

import argparse
class Formatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter): pass
cli_desc = globalz.get('?description', __doc__)
parser = argparse.ArgumentParser(description=cli_desc, formatter_class=Formatter)
parser._optionals.title = __import__('gettext').gettext('named arguments')
add = parser.add_argument
add('client_id', nargs='?')
add('client_secret', nargs='?')
add('--client-id', metavar='CLIENT_ID', dest='client_id_opt', help=argparse.SUPPRESS)
add('--client-secret', metavar='CLIENT_SECRET', dest='client_secret_opt', help=argparse.SUPPRESS)
add('--scope', default='*', help='an OAuth2 scope string')
add('--redirect-uri', default="http://localhost:8080", help="\N{ZERO WIDTH SPACE}")
if globalz.get('?access_token_only', False):
    add('--access-token-only', default=True, help=argparse.SUPPRESS)
else:
    add('--access-token-only', action='store_true', help="get an access token and not a refresh token")
add('--no-web-browser', action='store_true', help="don't launch a browser")
add('--web-browser-name', help="the web browser to open")
args = parser.parse_args()


import sys
import os
import re
import uuid
import socket
import urllib.parse
import webbrowser
import signal
from pprint import pp

import redditwarp
from redditwarp.http.transport.SYNC import load_transport
from redditwarp.core.SYNC import RedditTokenObtainmentClient
from redditwarp.core.reddit_http_client_SYNC import get_user_agent

def get_client_cred_input(prompt: str, env: str, v: Optional[str]) -> str:
    if v is None:
        v = input(prompt)
    if v == '.':
        v = os.environ[env]
        print(v)
    return v

def get_client_id(args: argparse.Namespace) -> str:
    v = args.client_id_opt or args.client_id
    return get_client_cred_input('Client ID: ', 'redditwarp_client_id', v)

def get_client_secret(args: argparse.Namespace) -> str:
    v = args.client_secret_opt or args.client_secret
    return get_client_cred_input('Client secret: ', 'redditwarp_client_secret', v)

def handle_sigint(sig: int, frame: Optional[FrameType]) -> None:
    print('KeyboardInterrupt', file=sys.stderr)
    sys.exit(130)

signal.signal(signal.SIGINT, handle_sigint)

ti = load_transport()

client_id = get_client_id(args)
client_secret = get_client_secret(args)
scope: str = args.scope
redirect_uri: str = args.redirect_uri
access_token_only: bool = args.access_token_only
no_web_browser: bool = args.no_web_browser
web_browser_name: Optional[str] = args.web_browser_name

state = str(uuid.uuid4())
browser = webbrowser.get(web_browser_name)

print('\n        -~=~- Reddit OAuth2 Authorization Code Flow -~=~-\n')
print('* Step 1. Build the authorization URL and direct the user to the authorization server.\n')

params = {
    'response_type': 'code',
    'client_id': client_id,
    'redirect_uri': redirect_uri,
    'scope': scope,
    'state': state,
    'duration': 'temporary' if access_token_only else 'permanent',
}
url = f"{redditwarp.auth.const.AUTHORIZATION_URL}?{urllib.parse.urlencode(params)}"
print(url)
print()

if not no_web_browser:
    browser.open(url)

print('* Step 2. Wait for the authorization server response and extract the authorization code.\n')

print('Press Ctrl+C to abort the script if the authorization request was rejected.\n')

with socket.socket() as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('localhost', 8080))
    server.listen(1)
    match = None
    while not match:
        client, addr = server.accept()
        print('{0}:{1}'.format(*addr))
        with client:
            data = client.recv(8192)
            client.send(b"HTTP/1.1 200 OK\r\n\r\n" + data)

        decoded = data.decode()
        print(f"```\n{decoded}\n```\n")
        match = re.match(r"^GET /\?([^ ]*) HTTP", decoded)

assert match is not None
query = match[1]
response_params = dict(urllib.parse.parse_qsl(query))

received_state = response_params['state']
if received_state != state:
    raise Exception(f'sent state ({state}) did not match received ({received_state})')

code = response_params.get('code', '')
if not code:
    raise Exception('authorization was declined by the user')

print(f'Authorization code: {code}\n')

print('* Step 3. Exchange the authorization code for an access/refresh token.\n')

grant = redditwarp.auth.grants.AuthorizationCodeGrant(code, redirect_uri)
print('Authorization grant:')
pp(dict(grant))
print()

session = ti.new_session()
user_agent = get_user_agent(session) + " redditwarp.cli.refresh_token"
token_client = RedditTokenObtainmentClient(
    session,
    redditwarp.auth.const.TOKEN_OBTAINMENT_URL,
    (client_id, client_secret),
    grant,
    headers={'User-Agent': user_agent},
)

print('Obtaining token(s) from token server...\n')

token = token_client.fetch_token()

print(f'''\
     Access token: {token.access_token}
    Refresh token: {token.refresh_token}''')
