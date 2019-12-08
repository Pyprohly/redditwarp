
import redditwarp

client = redditwarp.Client()

response = client.request('GET', '/api/info', params={'id': 't1_d98khom'})
