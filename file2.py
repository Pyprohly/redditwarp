
from pprint import pprint

import redditwarp

def main():
	client = redditwarp.Client('GdfdxbF8ea73oQ', 'sOkVUjcTWNMZY11vWzlMAy4J7UE', username='Pyprohly', password='A2CVdajf2')
	while True:
		response = client.request('GET', '/api/v1/me')
		print({k: v for k, v in response.headers.items() if k.startswith('x-ratelimit')})

	client.close()

if __name__ == '__main__':
	main()
