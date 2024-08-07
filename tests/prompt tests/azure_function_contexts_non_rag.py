import os
from core.db.agent_db_base import AgentDBBase
from core.agent.agent_config import AgentConfig
import json
from langchain_community.document_loaders import TextLoader
from os.path import join
import logging
import urllib3
import requests

from  core.utils.schema import create_dynamic_model

urllib3.disable_warnings()

base_url = "http://localhost:7071/api"
#base_url = "https://deepthought-app.azurewebsites.net/api"

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

# quick schema test

policy = {
    "name": "ukho_policy",
    "description": "You are an AI assistant using the following passages to answer the user questions on policies and software coding standards at the UKHO (UK Hydrogrpahic Office). ",
    "role": "You should also use the content in any of the links in the passages as SOURCES. Each passage has a NAME which is the title of the document. After your answer, leave a blank line and then give the source html link(s) of the passages you answered from. Put them in a <br> separated list, prefixed with SOURCES and do not adjust the embedded html data in the source links:.",
    "expected_input": "a question about a UKHO software engineering policy or coding standard",
    "expected_output": "a detailed and specific job posting ",
    "output_format": [],
    "examples": [
        "Example: Question: What is the meaning of life? Response: The meaning of life is 42. SOURCES: <a href='https://some/web/reference>'>Hitchhiker's Guide to the Galaxy</a>"
    ],
    "options": {
        "rag_mode": True,
        "context": "github1",
        "icl_mode": True,
        "icl_context": "icl_test",
		"prefetch_tool_mode":True,
		"prefetch_role_mode":True,
		"prefetch_context_mode":True,
        "model_override":"groq:llama-3.1-405b-reasoning",
        "role_override":True,
        "role_override_context":"deepthoughtai",
        "use_structured_output":True,
        "use_reasoning":True
    },
    "level":"user"
}


SchemaModel = create_dynamic_model(policy)
schema_model = SchemaModel.schema_json(indent=2)
print(schema_model)



### Test Auth ####
headers = {
    'Content-Type': 'application/json',
    'x-user-id': 'ukho',
    'x-password': 'my_password'
    }

url = f"{base_url}/request_auth"
response = requests.get(url, headers=headers)

token = json.loads(response.content.decode('utf-8'))

### Create the a github reader for .role and .schema files ####
url = f"{base_url}/contexts_crud"
new_context = {
    "id": "deepthoughtai",
    "name": "deepthoughtai",
    "loader": "github_file_loader",
    "loader_args": {
        "repo": "Kirosoft/DeepThought",
        "access_token": "$GITHUB_ACCESS_TOKEN",
        "filter": [
            ".role",".schema"
        ],
        "api_url": "https://api.github.com"
    },
    "options": {},
    "adaptor": "html_to_text",
    "current_version": 1,
    "adaptor_args": {},
    "level": "user"
}


headers = {
    'Authorization': f'Bearer {token["token"]}',
    'Content-Type': 'application/json',
    'x-user-id': 'ukho'
    }

params = {'id': new_context["id"]}

# create a new context
payload = json.dumps(new_context, ensure_ascii=False).encode('utf8')
response = requests.post(url, payload, headers=headers)
response_json = response.json()
print(response_json)

# get the new context
response = requests.get(url, params=params, headers=headers)
response_json = response.json()
print(response_json)


# run the loader
url = f"{base_url}/run_context"
response = requests.get(url, params=params, headers=headers)
response_json = response.json()
print(response_json)

#test - a prompt using 'auto' role mode
document = {"input": "I would like to create a new role called quiz_master, this should generate 10 new pub quiz questions on a variety of topics","role":"auto", "name":"run_agent", "session_token":"this_should_be_random"}

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

