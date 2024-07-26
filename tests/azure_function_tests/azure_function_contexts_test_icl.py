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
pre_auth_headers = {
    'Content-Type': 'application/json',
    'x-user-id': 'ukho',
    'x-password': 'my_password'
    }

url = "http://localhost:7071/api/request_auth"
response = requests.get(url, headers=pre_auth_headers)

token = json.loads(response.content.decode('utf-8'))

### Test Agent Execution ####

contexts_crud_url = "http://localhost:7071/api/contexts_crud"
contexts_run_url = "http://localhost:7071/api/run_context"

def create_context(name, urls):
    return {
        "id": name,
        "tenant": "ukho",
        "user_id": "ukho",
        "data_type": "context_definition",
        "name": name,
        "loader": "text_file_loader",
        "loader_args": {
            "url": ",".join(urls),
        },
        "adaptor": "html_to_text",
        "adaptor_args": {},
        "current_version":0,
        "rag_options": {
            "chunk_size": 5,
            "chunk_overlap": 0,
            "separator": "@",
            "strategy": "CharacterTextSplitter",
            "is_regex": False        
        }
    }

urls = [
    "https://raw.githubusercontent.com/Kirosoft/DeepThoughtData/main/icl_test_data.txt"
]
icl_test_context = create_context('icl_test',urls)

headers_post_auth = {
        'Authorization': f'Bearer {token["token"]}',
        'Content-Type': 'application/json',
        'x-user-id': 'ukho'
    }

# create a new context
payload = json.dumps(icl_test_context, ensure_ascii=False).encode('utf8')
response = requests.post(contexts_crud_url, payload, headers=headers_post_auth)
response_json = response.json()
print(response_json)

# run the context loader
response = requests.get(contexts_run_url, params={"id":icl_test_context["id"]}, headers=headers_post_auth)
response_json = response.json()
print(response_json)

