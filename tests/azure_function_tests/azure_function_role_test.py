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

url = "http://localhost:7071/api/roles"
new_role = {
    "name":"test_role",
    "description":"You are an AI assistant using the following passages to answer the user questions on policies at the UKHO (UK Hydrogrpahic Office). ",
    "role":"You should also use the content in any of the links in the passages as SOURCES. Each passage has a NAME which is the title of the document. After your answer, leave a blank line and then give the source html link(s) of the passages you answered from. Put them in a <br> separated list, prefixed with SOURCES and do not adjust the embedded html data in the source links:.",
    "expected_input":"a question about a UKHO policy",
    "expected_output":"a detailed and specific job posting ",
    "output_format":[],
    "examples":["Example: Question: What is the meaning of life? Response: The meaning of life is 42. SOURCES: <a href='https://some/web/reference>'>Hitchhiker's Guide to the Galaxy</a>"],
    "tools":[],
    "options":
        {
            "rag_mode":True
        },
    "supervisor":[],
    "assistants":[]
}


headers = {
    'Authorization': f'Bearer {token["token"]}',
    'Content-Type': 'application/json',
    'x-user-id': '12345'
    }

params = {'id': "test_role"}

# create a new user role
payload = json.dumps(new_role, ensure_ascii=False).encode('utf8')
response = requests.post(url, payload, headers=headers)
response_json = response.json()
print(response_json)

# get the new role
response = requests.get(url, params=params, headers=headers)
response_json = response.json()
print(response_json)

# delete the new role
response = requests.delete(url, params=params, headers=headers)
response_json = response.json()
print(response_json)


# get the  role (should be blank)
response = requests.get(url, params=params, headers=headers)
response_json = response.json()
print(response_json)


# get the  all the roles
response = requests.get(url, headers=headers)
response_json = response.json()
print(response_json)



