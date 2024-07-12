import json
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
headers = {
    'Authorization': f'Bearer {token["token"]}',
    'Content-Type': 'application/json',
    'x-user-id': '12345'
    }

new_flow = {
    "last_node_id": 3,
    "last_link_id": 2,
    "nodes": [
        {
            "id": 1,
            "type": "basic/input",
            "pos": {
                "0": 212,
                "1": 258,
                "2": 0,
                "3": 0,
                "4": 0,
                "5": 0,
                "6": 0,
                "7": 0,
                "8": 0,
                "9": 0
            },
            "size": {
                "0": 210,
                "1": 58
            },
            "flags": {},
            "order": 0,
            "mode": 0,
            "inputs": [],
            "outputs": [
                {
                    "name": "UserText",
                    "type": "text",
                    "links": [
                        1
                    ],
                    "slot_index": 0
                }
            ],
            "title": "Input",
            "properties": {
                "output": "multiline"
            },
            "widgets_values": [
                "multiline"
            ]
        },
        {
            "id": 3,
            "type": "basic/output",
            "pos": {
                "0": 1028,
                "1": 354,
                "2": 0,
                "3": 0,
                "4": 0,
                "5": 0,
                "6": 0,
                "7": 0,
                "8": 0,
                "9": 0
            },
            "size": {
                "0": 360,
                "1": 266
            },
            "flags": {},
            "order": 2,
            "mode": 0,
            "inputs": [
                {
                    "name": "Input Request", 
                    "type": "text",
                    "link": 2
                },
                {
                    "name": "Context",
                    "type": "text",
                    "link": None
                },
                {
                    "name": "Examples",
                    "type": "text",
                    "link": None
                }
            ],
            "outputs": [
                {
                    "name": "Answer",
                    "type": "text",
                    "links": None
                }
            ],
            "properties": {

            },
            "widgets_values": [

            ]
        },
        {
            "id": 2,
            "type": "roles/ukho_policy",
            "pos": {
                "0": 564,
                "1": 292,
                "2": 0,
                "3": 0,
                "4": 0,
                "5": 0,
                "6": 0,
                "7": 0,
                "8": 0,
                "9": 0
            },
            "size": {
                "0": 210,
                "1": 106
            },
            "flags": {},
            "order": 1,
            "mode": 0,
            "inputs": [
                {
                    "name": "Input Request",
                    "type": "text",
                    "link": 1
                }
            ],
            "outputs": [
                {
                    "name": "Answer",
                    "type": "text",
                    "links": None
                }
            ],
            "title": "UKHOPolicy",
            "properties": {
                "flows": "ukho"
            },
            "widgets_values": [
                0.5,
                "default",
                "multiline"
            ]
        }
    ],
    "links": [
        [
            1,
            1,
            0,
            2,
            0,
            "text"
        ],
        [
            2,
            2,
            0,
            3,
            0,
            "text"
        ]
    ],
    "groups": [],
    "config": {},
    "extra": {},
    "version": 0.4,
    "name": "test_flow",
    "level": "user",
    "id": "test_flow",
    "data_type": "flows",
    "tenant": "ukho",
    "user_id": "12345"
}

params = {'id': new_flow["name"]}
url = "http://localhost:7071/api/flows_crud"

# create a new user flows
payload = json.dumps(new_flow, ensure_ascii=False).encode('utf8')
response = requests.post(url, payload, headers=headers)
response_json = response.json()
print(response_json)

#############################################
# run the contexts orchestrator
url = "http://localhost:7071/api/run_flow"
response = requests.get(url, params=params, headers=headers)
response_json = response.json()
print(response_json)

instance_id = response_json["id"]

# raise the completion event
params = {'instance_id': instance_id, 'question':'what is the coding policy for javascript', 'flow_name':new_flow["name"]}
url = "http://localhost:7071/api/completion"
response = requests.get(url, params=params, headers=headers)
response_json = response.json()
print(response_json)
