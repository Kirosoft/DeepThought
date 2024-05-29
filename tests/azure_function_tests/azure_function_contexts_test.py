import os
from core.db.agent_db_base import AgentDBBase
from core.agent.agent_config import AgentConfig
import json
from langchain_community.document_loaders import TextLoader
from os.path import join
import logging
import urllib3
import requests


urllib3.disable_warnings()

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

### Test Auth ####
headers = {
    'Content-Type': 'application/json',
    'x-user-id': '12345',
    'x-password': 'my_password'
    }

url = "http://localhost:7071/api/request_auth"
response = requests.get(url, headers=headers)

token = json.loads(response.content.decode('utf-8'))

### Test Agent Execution ####

url = "http://localhost:7071/api/contexts_crud"
new_context = {
    "id": "github1",
    "tenant": "ukho",
    "user_id": "12345",
    "data_type": "context_ukho_policy_v1",
    "name": "github1",
    "loader": "github_file_loader",
    "loader_args": {
        "repo": "ukho/docs",
        "access_token": "$GITHUB_ACCESS_TOKEN",
        "file_filter": ".md",
        "api_url": "https://api.github.com"
    },
    "adaptor": "html_to_text",
    "adaptor_args": {},
    "rag_options": {
        "chunk_size": 1000,
        "overlap": 250,
        "strategy": "basic"
    }
}


headers = {
    'Authorization': f'Bearer {token["token"]}',
    'Content-Type': 'application/json',
    'x-user-id': '12345'
    }

params = {'id': "github1"}

# create a new context
payload = json.dumps(new_context, ensure_ascii=False).encode('utf8')
response = requests.post(url, payload, headers=headers)
response_json = response.json()
print(response_json)

# get the new context
response = requests.get(url, params=params, headers=headers)
response_json = response.json()
print(response_json)

# get the  all the contexts
response = requests.get(url, headers=headers)
response_json = response.json()
print(response_json)


# delete the new context
response = requests.delete(url, params=params, headers=headers)
response_json = response.json()
print(response_json)


# get the  context (should be blank)
response = requests.get(url, params=params, headers=headers)
response_json = response.json()
print(response_json)



