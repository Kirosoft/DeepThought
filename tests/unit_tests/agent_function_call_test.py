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

from core.agent.agent_role import AgentRole


agent_role = AgentRole("12345", "ukho")
document = {"input": "what is the weather","role":"weather_forecast"}

result = agent_role.run_agent(json.dumps(document))

print(result)

document = {"input": "the location is plymouth, UK","role":"weather_forecast", "session_token":result["session_token"]}

result = agent_role.run_agent(json.dumps(document))

print(result)

