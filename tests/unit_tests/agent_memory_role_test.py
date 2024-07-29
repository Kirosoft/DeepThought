import os
import json
from langchain_community.document_loaders import TextLoader
from os.path import join
import logging
import urllib3

from core.agent.agent_memory_role import AgentMemoryRole
from core.security.security_utils import get_user_context

urllib3.disable_warnings()

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

# take the local settgins file and convert it into environemnt variables
settings = json.loads(TextLoader(join(os.getcwd(), 'local.settings.json'), encoding="utf-8").load()[0].page_content)

for setting in settings["Values"]:
    os.environ[setting]=settings["Values"][setting]

from core.agent.agent_config import AgentConfig

user_settings = get_user_context('ukho')

agent_config = AgentConfig(user_settings_keys = user_settings["keys"])
agent_memory_role = AgentMemoryRole(agent_config, "ukho", "ukho")


top_role = agent_memory_role.get_context("is this valid :{'Authorization': Bearer 123651263712351','Content-Type': 'application/json','x-user-id': ''}")
print(top_role)


top_role = agent_memory_role.get_context("what is the coding policy on c#")
print(top_role)




