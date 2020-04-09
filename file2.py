
import sys
import os
import redditwarp

def main():
	try:
		client = redditwarp.Client(
			os.environ['redditwarp_client_id'],
			os.environ['redditwarp_client_secret'],
			username=os.environ['redditwarp_username'],
			password=os.environ['redditwarp_password']+'e',
		)
		data = client.request('GET', '/api/v1/me')

	finally:
		globals().update(locals())

if __name__ == '__main__':
	main()
