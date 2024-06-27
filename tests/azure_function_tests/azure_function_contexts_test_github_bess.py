import os
from core.db.agent_db_base import AgentDBBase
from core.agent.agent_config import AgentConfig
from core.security.security_utils import get_user_context
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

base_url = "http://localhost:7071/api"
#base_url = "https://deepthought-app.azurewebsites.net/api"


# take the local settgins file and convert it into environemnt variables
settings = json.loads(TextLoader(join(os.getcwd(), 'local.settings.json'), encoding="utf-8").load()[0].page_content)

for setting in settings["Values"]:
    os.environ[setting]=settings["Values"][setting]


### Test Auth ####
headers = {
    'Content-Type': 'application/json',
    'x-user-id': '12345',
    'x-password': 'my_password'
    }

url = f"{base_url}/request_auth"
response = requests.get(url, headers=headers)

token = json.loads(response.content.decode('utf-8'))

### Test Agent Execution ####

url = f"{base_url}/contexts_crud"

new_context = {
    "id": "bess",
    "tenant": "ukho",
    "user_id": "12345",
    "data_type": "context_definition",
    "name": "bess",
    "loader": "github_file_loader",
    "loader_args": {
        "repo": "kirosoft/bess",
        "access_token": "$GITHUB_ACCESS_TOKEN",
        "filter": ".json",
        "api_url": "https://api.github.com"
    },
    "adaptor": "html_to_text",
    "current_version":0,
    "adaptor_args": {},
    "rag_options": {
        "chunk_size": 1000,
        "overlap": 250,
        "strategy": "basic"
    }
}


headers = {
    'Authorization': f'Bearer {token["token"]}',
    'Content-Type': 'application/json',
    'x-user-id': '12345'
    }

params = {'id': "bess"}

# # create a new context
# payload = json.dumps(new_context, ensure_ascii=False).encode('utf8')
# response = requests.post(url, payload, headers=headers)
# response_json = response.json()
# print(response_json)

# # get the new context
# response = requests.get(url, params=params, headers=headers)
# response_json = response.json()
# print(response_json)


#############################################
# run the contexts orchestrator
url = f"{base_url}/run_context"
# response = requests.get(url, params=params, headers=headers)
# response_json = response.json()
# print(response_json)

json_validator_role = {
    "name": "json_validator",
    "role": "You are a helpful AI assistant that is expert in ensuring that the JSON input is syntactically correct and is valid based on the examples provided.",
    "expected_input": "a valid JSON input is expected which will reference some ENCs (chart areas) and will contain some jon scheduling information.",
    "expected_output": "valid json output is expected",
    "output_format": [],
    "examples": ["$bess"],
    "tools": [],
    "options": {
        "rag_mode": True
    },
    "input": "what are the usability standards",
    "session_token": "",
    "level": "user",
    "id": "json_validator",
    "ttl": -1
}

# create a new user role
url = f"{base_url}/roles_crud"
payload = json.dumps(json_validator_role, ensure_ascii=False).encode('utf8')
response = requests.post(url, payload, headers=headers)
response_json = response.json()
print(response_json)


# run_agent
url = f"{base_url}/run_agent"
json_test_payload = """

    "name": "SDJames01",
    "exchangeSetStandard": "s63",
    "encCellNames": {
        "GB123456",
        "GB123457",
        "GB123458"
    ],
    "frequency": "00 12 * * 4",
	"frequency_description": "At 17:00 on Wednesday. UTC TIME."
    "type": "BASE",
    "keyFileType": "NONE",
    "allowedUsers": [],
    "allowedUserGroups": ["SDRA"
    ],
    "tags": [
        {
            "key": "Exchange Set Type",
            "value": "Base"
        },
        {
            "key": "Audience",
            "value": "FSS/SDRA"
        },
		{
            "key": "Audience",
            "value": "FSS/SDRA"
        },
        {
            "key": "Frequency",
            "value": "Weekly"
        },
        {
            "key": "Product Type"
            "value": "AVCS"
        },
        {
            "key": "Media Type",
            "value": "Zip"
        },
        {
            "key": "S63 Version",
            "value": "1.2"
        },
        {
            "key": "Year",
            "value": "$(now.WeekNumber.Year)"
        },
        {
            "key": "Week Number",
            "value": "$(now.WeekNumber)"
        },
        {
            "key": "Year / Week",
            "value": "$(now.WeekNumber.Year) / $(now.WeekNumber2)"
        }
    ],
    "readMeSearchFilter": "NONE",
    "batchExpiryInDays": 8,
    "isEnabled": "Yes"
}
"""
document = {"input": f"please check that this JSON is valid: {json_test_payload}","role":"json_validator", "name":"run_agent"}
payload = json.dumps(document, ensure_ascii=False).encode('utf8')

response = requests.post(url, payload, headers=headers)
response_json = response.json()
