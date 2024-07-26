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
    'x-user-id': 'ukho',
    'x-password': 'my_password'
    }

url = "http://localhost:7071/api/request_auth"
response = requests.get(url, headers=headers)

token = json.loads(response.content.decode('utf-8'))

### Test Agent Execution ####
headers = {
    'Authorization': f'Bearer {token["token"]}',
    'Content-Type': 'application/json',
    'x-user-id': 'ukho'
    }

new_flow = {
    "last_node_id": 6,
    "last_link_id": 5,
    "nodes": [
        {
            "id": 4,
            "type": "context/github1",
            "pos": {
                "0": 196,
                "1": 703,
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
            "order": 0,
            "mode": 0,
            "inputs": [
                {
                    "name": "trigger",
                    "type": -1,
                    "link": None
                }
            ],
            "outputs": [
                {
                    "name": "context_definition",
                    "type": "text",
                    "links": [3]
                }
            ],
            "title": "UKHOPolicy",
            "properties": {
                "context_definition": "github1"
            },
            "widgets_values": [
                0.5
            ]
        },
        {
            "id": 2,
            "type": "role/ukho_policy",
            "pos": {
                "0": 582,
                "1": 188,
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
            "order": 3,
            "mode": 0,
            "inputs": [
                {
                    "name": "input",
                    "type": "text",
                    "link": 1
                },
                {
                    "name": "context",
                    "type": "text",
                    "link": 3
                },
                {
                    "name": "icl_context",
                    "type": "text",
                    "link": 5
                }
            ],
            "outputs": [
                {
                    "name": "answer",
                    "type": "text",
                    "links": [
                        2
                    ]
                }
            ],
            "title": "UKHOPolicy",
            "properties": {
                "name": "ukho policy",
                "role": "You are an AI assistant using the following passages to answer the user questions on policies at the UKHO (UK Hydrogrpahic Office). You should also use the content in any of the links in the passages as SOURCES. Each passage has a NAME which is the title of the document. After your answer, leave a blank line and then give the source html link(s) of the passages you answered from. Put them in a <br> separated list, prefixed with SOURCES and do not adjust the embedded html data in the source links:.",
                "expected_input": "a question about a UKHO policy",
                "expected_output": "a detailed and specific job posting ",
                "output_format": [],
                "examples": [
                    "Example: Question: What is the meaning of life? Response: The meaning of life is 42. SOURCES: <a href='https://some/web/reference>'>Hitchhiker's Guide to the Galaxy</a>"
                ],
                "tools": [],
                "options": {
                    "rag_mode": True
                },
                "input": "what are the usability standards",
                "answer": "",
                "session_token": "",
                "flows": "ukho",
                "type": "text"
            },
            "widgets_values": [
                0.5,
                "default",
                "multiline",
                "a detailed and specific job posting ",
                [],
                [],
                "default",
                "default"
            ]
        },
        {
            "id": 1,
            "type": "basic/input",
            "pos": {
                "0": 168,
                "1": 191,
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
            "order": 1,
            "mode": 0,
            "inputs": [],
            "outputs": [
                {
                    "name": "userinput",
                    "type": "text",
                    "links": [
                        1
                    ],
                    "slot_index": 0
                }
            ],
            "title": "Input",
            "properties": {
                "output": "text",
                "type": "text"
            }
        },
        {
            "id": 3,
            "type": "basic/output",
            "pos": {
                "0": 1138,
                "1": 349,
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
                "0": 290,
                "1": 26
            },
            "flags": {},
            "order": 4,
            "mode": 0,
            "inputs": [
                {
                    "name": "input",
                    "type": "text",
                    "link": 2
                }
            ],
            "outputs": [],
            "properties": {}
        },
        {
            "id": 5,
            "type": "events/timer",
            "pos": [
                -78,
                619
            ],
            "size": {
                "0": 140,
                "1": 26
            },
            "flags": {},
            "order": 2,
            "mode": 0,
            "outputs": [
                {
                    "name": "on_tick",
                    "type": -1,
                    "links": [4],
                    "slot_index": 0
                }
            ],
            "properties": {
                "interval": 60*60,
                "event": "tick"
            },
            "boxcolor": "#222"
        },
        {
            "id": 6,
            "type": "context/icl_test",
            "pos": {
                "0": 350,
                "1": 703,
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
            "order": 0,
            "mode": 0,
            "inputs": [
                {
                    "name": "trigger",
                    "type": -1,
                    "link": None
                }
            ],
            "outputs": [
                {
                    "name": "context_definition",
                    "type": "text",
                    "links": [3]
                }
            ],
            "title": "ICL Test",
            "properties": {
                "context_definition": "icl_test"
            },
            "widgets_values": [
                0.5
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
        ],
        [
            3,
            4,
            0,
            2,
            0,
            "text"
        ],
        [
            4,
            5,
            0,
            4,
            0,
            -1
        ],
        [
            5,
            6,
            0,
            4,
            0,
            -1
        ]
    ],
    "groups": [],
    "config": {},
    "extra": {},
    "version": 0.4,
    "name": "test_flow",
    "level": "user",
    "id": "test_flow",
}

params = {'id': new_flow["name"]}
url = "http://localhost:7071/api/flows_crud"

# # create a new user flows
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


# raise another completion event
params = {'instance_id': instance_id, 'question':'what is the coding policy for c#', 'flow_name':new_flow["name"]}
url = "http://localhost:7071/api/completion"
response = requests.get(url, params=params, headers=headers)
response_json = response.json()
print(response_json)
