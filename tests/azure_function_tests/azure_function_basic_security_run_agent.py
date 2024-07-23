import os

import json
import logging
import urllib3
import requests

urllib3.disable_warnings()

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

headers = {
    'Content-Type': 'application/json',
    'x-user-id': 'ukho',
    'x-password': 'my_password'
    }

#base_url = "http://localhost:7071/api"
base_url = "https://deepthought-app.azurewebsites.net/api"

url = f"{base_url}/request_auth"
response = requests.get(url, headers=headers)

token = json.loads(response.content.decode('utf-8'))


document = {"input": "what are the github policies","role":"ukho_policy", "name":"run_agent", "session_token":"test_session_token_must_be_16"}

headers = {
    'Authorization': f'Bearer {token["token"]}',
    'Content-Type': 'application/json',
    'x-user-id': 'ukho'
    }
payload = json.dumps(document, ensure_ascii=False).encode('utf8')

url = f"{base_url}/run_agent"
response = requests.post(url, payload, headers=headers)
response_json = response.json()
print(response_json)


# delete session
document = {"name":"clear_session", "session_token":"test_session"}
url = f"{base_url}/clear_session"
response = requests.post(url, payload, headers=headers)
print(response_json)

