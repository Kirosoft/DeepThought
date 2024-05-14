import os
import json
from langchain_community.document_loaders import TextLoader
from os.path import join
import logging
import urllib3

urllib3.disable_warnings()

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

# take the local settgins file and convert it into environemnt variables
settings = json.loads(TextLoader(join(os.getcwd(), 'local.settings.json'), encoding="utf-8").load()[0].page_content)

for setting in settings["Values"]:
    os.environ[setting]=settings["Values"][setting]

from core.db.agent_db_base import AgentDBBase
from core.agent.agent_config import AgentConfig
from core import process_request

agent_config = AgentConfig()

document = {"input": "what is the weather","role":"weather_forecast"}

result = process_request(json.dumps(document), "12345", "ukho")

print(result)

document = {"input": "the location is plymouth, UK","role":"weather_forecast", "session_token":result["session_token"]}

result = process_request(json.dumps(document), "12345", "ukho")

print(result)

