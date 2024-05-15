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

from core.agent.agent_config import AgentConfig
from core.middleware.role import Role

agent_config = AgentConfig()
user_role = Role(agent_config, "12345", "ukho")


all_roles = user_role.load_all_roles()

## we should get user and system roles
print(all_roles)

### create a new system role

system_roles = Role(agent_config, "system", "system")

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


### check system role saves
result = system_roles.save_role(new_role)

print(f"Saved system new role: {result}")

result = system_roles.get_role(new_role["name"])

print(f"Retrieved system role: ",result)
### do some assert stuff here

result = system_roles.delete_role(new_role["name"])
print(f"Deleted system {result}")

result = system_roles.get_role(new_role["name"])

print("Retrieved system role: ",result)

### check user role saves
result = user_role.save_role(new_role)

print(f"Saved new user role: {result}")

result = user_role.get_role(new_role["name"])

print(f"Retrieved user role: ",result)
### do some assert stuff here

result = user_role.delete_role(new_role["name"])
print(f"Deleted user role {result}")

result = user_role.get_role(new_role["name"])

print("Retrieved user role: ",result)

