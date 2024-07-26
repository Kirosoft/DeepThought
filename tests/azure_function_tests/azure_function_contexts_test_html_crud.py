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
    "id": "s57_enc_catalogue",
    "tenant": "ukho",
    "user_id": "12345",
    "data_type": "context_definition",
    "name": "s57_enc_catalogue",
    "loader": "html_file_loader",
    "loader_args": {
        "url": "https://www.teledynecaris.com/s-57/frames/S57catalog.htm",
    },
    "adaptor": "html_to_text",
    "adaptor_args": {},
    "current_version":0,
    "rag_options": {
        "chunk_size": 1000,
        "chunk_overlap": 250,
        "separator": "\n\n",
        "strategy": "CharacterTextSplitter",
        "is_regex": False        
    }
}


headers = {
    'Authorization': f'Bearer {token["token"]}',
    'Content-Type': 'application/json',
    'x-user-id': '12345'
    }

params = {'id': "s57_enc_catalogue"}

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
# response = requests.delete(url, params=params, headers=headers)
# response_json = response.json()
# print(response_json)


# get the  context (should be blank)
response = requests.get(url, params=params, headers=headers)
response_json = response.json()
print(response_json)

