import os
from core.db.agent_db_base import AgentDBBase
from core.agent.agent_config import AgentConfig
import json
from langchain_community.document_loaders import TextLoader
from os.path import join
from core import process_request
import logging
import urllib3
import requests

urllib3.disable_warnings()

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

# take the local settgins file and convert it into environemnt variables
settings = json.loads(TextLoader(join(os.getcwd(), 'local.settings.json'), encoding="utf-8").load()[0].page_content)

for setting in settings["Values"]:
    os.environ[setting]=settings["Values"][setting]

agent_config = AgentConfig()

document = {"input": "what is the policy on code pairing","role":"ukho_policy", "name":"core_llm_agent"}

url = "http://localhost:7071/api/core_llm_agent"
payload = json.dumps(document, ensure_ascii=False).encode('utf8')

response = requests.post(url, payload)
response_json = response.json()
print(response_json)
