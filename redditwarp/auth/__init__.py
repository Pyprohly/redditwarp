
from urllib.parse import urlencode

def authorization_url(
	url,
	response_type,
	client_id,
	redirect_uri,
	scopes,
	state,
	extra_params,
):
	params = {
		'response_type': response_type,
		'client_id': client_id,
		'redirect_uri': redirect_uri,
		'scope': scopes,
		'state': state,
		**extra_params,
	}
	return '%s?%s' % (url, urlencode(params))
 