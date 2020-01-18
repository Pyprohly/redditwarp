
import os
import redditwarp

def main():
	client = redditwarp.Client(
		os.environ['redditwarp_client_id'],
		os.environ['redditwarp_client_secret'],
		os.environ['redditwarp_refresh_token'],
	)
	while True:
		response = client.request('GET', '/api/v1/me')
		print({k: v for k, v in response.headers.items() if k.startswith('x-ratelimit')})

	client.close()

if __name__ == '__main__':
	main()
