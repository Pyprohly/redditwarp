
from pprint import pprint

import redditwarp

def main():
	with (
		redditwarp.Client('GdfdxbF8ea73oQ', 'sOkVUjcTWNMZY11vWzlMAy4J7UE', username='Pyprohly', password='A2CVdajf2')
	) as client:
		'''
		response = client.request('GET', '/api/v1/me')
		pprint(response.data)
		'''
		data = client.request_json('GET', '/api/v1/me')
		pprint(data)

	globals().update(locals())

if __name__ == '__main__':
	main()
