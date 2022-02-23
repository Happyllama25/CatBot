from async_timeout import timeout
import requests, os
from dotenv import load_dotenv
load_dotenv('config.env')

API_KEY = os.getenv('API_KEY')
#servers/019e4728/resources
url = 'https://panel.happyllama25.net/api/client/servers/019e4728/resources'
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

# data = requests.request('GET', url, headers=headers, timeout=10).json()
# server_names = []

# for server in data['data']:

#     server_names.append(server['attributes'] ['name'])


# server_identifiers = []

# for server in data['data']:

#     server_identifiers.append(server['attributes'] ['identifier'])


# server_id = '\n'.join(server_identifiers)

# server_names = '\n'.join(server_names)

# print(server_id)


# print(server_names)









id = '019e4728'

url = f'https://panel.happyllama25.net/api/client/servers/{id}'
data = requests.request('GET', url, headers=headers).json()


server_status = []

for server in data['attributes']['relationships']['allocations']['data']:

    server_status = server['attributes']['ip_alias']

# print(dataname)
print(server_status)

