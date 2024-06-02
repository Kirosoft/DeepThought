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

def create_context(name, url):
    return {
        "id": name,
        "tenant": "ukho",
        "user_id": "12345",
        "data_type": "context_definition",
        "name": name,
        "loader": "pdf_file_loader",
        "loader_args": {
            "url": url,
        },
        "adaptor": "html_to_text",
        "adaptor_args": {},
        "current_version":0,
        "rag_options": {
            "chunk_size": 1000,
            "overlap": 250,
            "strategy": "basic"
        }
    }



iho_object_catalogue = create_context("iho_object_catalogue","https://iho.int/uploads/user/pubs/standards/s-57/31ApAch1.pdf")
iho_attribute_catalogue = create_context("iho_attribute_catalogue", "https://iho.int/uploads/user/pubs/standards/s-57/31ApAch2.pdf")
iho_attribute_object_cross_reference = create_context("iho_attribute_object_cross_reference", "https://iho.int/uploads/user/pubs/standards/s-57/31XREF.pdf")
iho_s57_product_specification = create_context("iho_s57_product_specification", "https://iho.int/uploads/user/pubs/standards/s-57/20ApB1.pdf")
iho_s57_product_supplement_3 = create_context("iho_s57_product_supplement","https://iho.int/uploads/user/pubs/standards/s-57/S-57_e3.1_Supp3_Jun14_EN.pdf")
s57_sources = [iho_object_catalogue, iho_attribute_catalogue, iho_attribute_object_cross_reference, iho_s57_product_specification, iho_s57_product_supplement_3]

headers_post_auth = {
    'Authorization': f'Bearer {token["token"]}',
    'Content-Type': 'application/json',
    'x-user-id': '12345'
    }

for source in s57_sources:
    # create a new context
    payload = json.dumps(source, ensure_ascii=False).encode('utf8')
    response = requests.post(contexts_crud_url, payload, headers=headers_post_auth)
    response_json = response.json()
    print(response_json)

    response = requests.get(contexts_run_url, params={"id":source["id"]}, headers=headers_post_auth)
    response_json = response.json()
    print(response_json)

