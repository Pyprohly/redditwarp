
from pprint import pprint

import redditwarp

def main():
	client = redditwarp.Client('GdfdxbF8ea73oQ', 'sOkVUjcTWNMZY11vWzlMAy4J7UE', username='Pyprohly', password='A2CVdajf2')
	#response = client.request('GET', '/api/info', params={'id': 't1_d98khom'})
	response = client.request('GET', '/api/v1/me')
	pprint(response.data)
	client.close()

if __name__ == '__main__':
	main()
