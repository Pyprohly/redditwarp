
from redditwarp.auth.helper import TOKEN_ENDPOINT
from redditwarp.auth.grant import ClientCredentialsGrant
from redditwarp.auth.client import TokenClient, ClientCredentials
from redditwarp.http.transport.requests import Session

grant = ClientCredentialsGrant(scope='a v')
client_credentials = ClientCredentials('GdfdxbF8ea73oQ', 'sOkVUjcTWNMZY11vWzlMAy4J7UE')
session = Session()
session.headers['User-Agent'] = 'RedditWarp authorization code flow script'
token_client = TokenClient(session, TOKEN_ENDPOINT, client_credentials, grant)

print('Fetching token...')
print()
token = token_client.fetch_token()
print(vars(token))
