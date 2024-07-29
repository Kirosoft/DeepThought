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

headers = {
    'Authorization': f'Bearer {token["token"]}',
    'Content-Type': 'application/json',
    'x-user-id': 'ukho'
    }

params = {'id': "autorole"}
url = f"{base_url}/roles_crud"


# try to get the ukho policy
response = requests.get(url, params=params, headers=headers)
response_json = response.json()

if response.status_code == 200 and response_json == None:
    auto_role = {
        "name":"autorole",
        "description":"you are an AI assistant that will route the input query to the most applicable agent",
        "role":"You will use the description of the roles below to select the most suitable agent",
        "expected_input":"a question or input from the user",
        "expected_output":"a suitable role or None if no relevant role could be found",
        "output_format":[],
        "examples":[],
        "tools":[],
        "options":
            {
                "rag_mode":True
            },
        "supervisor":[],
        "assistants":[]
    }
    payload = json.dumps(auto_role, ensure_ascii=False).encode('utf8')
    response = requests.post(f"{base_url}/roles_crud", payload, headers=headers)
    response_json = response.json()




print(response_json)



