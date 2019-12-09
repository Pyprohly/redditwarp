
import time
import redditwarp

start_time = time.time()

client = redditwarp.Client('GdfdxbF8ea73oQ', 'sOkVUjcTWNMZY11vWzlMAy4J7UE')

response = client.request('GET', '/api/info', params={'id': 't1_d98khom'})
