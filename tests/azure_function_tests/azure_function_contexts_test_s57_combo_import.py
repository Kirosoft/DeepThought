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
    'x-user-id': '12345',
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
        "user_id": "12345",
        "data_type": "context_definition",
        "name": name,
        "loader": "pdf_file_loader",
        "loader_args": {
            "url": ",".join(urls),
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

urls = [
    "https://iho.int/uploads/user/pubs/standards/s-57/31ApAch1.pdf",
    "https://iho.int/uploads/user/pubs/standards/s-57/31ApAch2.pdf",
    "https://iho.int/uploads/user/pubs/standards/s-57/31XREF.pdf",
    "https://iho.int/uploads/user/pubs/standards/s-57/20ApB1.pdf",
    "https://iho.int/uploads/user/pubs/standards/s-57/S-57_e3.1_Supp3_Jun14_EN.pdf"
]
context_definition_s57 = create_context('s57',urls)

headers_post_auth = {
    'Authorization': f'Bearer {token["token"]}',
    'Content-Type': 'application/json',
    'x-user-id': '12345'
    }

# create a new context
payload = json.dumps(context_definition_s57, ensure_ascii=False).encode('utf8')
response = requests.post(contexts_crud_url, payload, headers=headers_post_auth)
response_json = response.json()
print(response_json)

# run the context loader
response = requests.get(contexts_run_url, params={"id":context_definition_s57["id"]}, headers=headers_post_auth)
response_json = response.json()
print(response_json)

