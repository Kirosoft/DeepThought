import os
from core.agent.agent_config import AgentConfig
from langchain_community.document_loaders import TextLoader
from core.middleware.flow import Flow
from os.path import join
import logging
import urllib3
import json

urllib3.disable_warnings()

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

# take the local settgins file and convert it into environemnt variables
settings = json.loads(TextLoader(join(os.getcwd(), 'local.settings.json'), encoding="utf-8").load()[0].page_content)

for setting in settings["Values"]:
    os.environ[setting]=settings["Values"][setting]


agent_config = AgentConfig()

flow = Flow(agent_config, "12345", "ukho")

# Example graph: A dictionary where key is the node, value is list of nodes dependent on the key
graph = {
    'D': ['E'],
    'C': [],
    'B': ['C', 'D'],
    'A': ['B'],
    'E': []
}

flow1 = {
    "last_node_id": 9,
    "last_link_id": 7,
    "nodes": [
        {
            "id": 8,
            "type": "roles/test_role",
            "pos": {
                "0": 1031,
                "1": 128,
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
                    "name": "Input Request",
                    "type": "text",
                    "link": 4
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
            "title": "E",
            "properties": {
                "name": "E",
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
                "session_token": ""
            },
            "widgets_values": [
                "You are an AI assistant using the following passages to answer the user questions on policies at the UKHO (UK Hydrogrpahic Office). You should also use the content in any of the links in the passages as SOURCES. Each passage has a NAME which is the title of the document. After your answer, leave a blank line and then give the source html link(s) of the passages you answered from. Put them in a <br> separated list, prefixed with SOURCES and do not adjust the embedded html data in the source links:.",
                [
                    "Example: Question: What is the meaning of life? Response: The meaning of life is 42. SOURCES: <a href='https://some/web/reference>'>Hitchhiker's Guide to the Galaxy</a>"
                ],
                "a question about a UKHO policy",
                "a detailed and specific job posting ",
                [],
                [],
                "default",
                "default"
            ]
        },
        {
            "id": 4,
            "type": "input",
            "pos": {
                "0": -85,
                "1": 116,
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
            "order": 0,
            "mode": 0,
            "inputs": [
                {
                    "name": "Input Request",
                    "type": "text",
                    "link": None
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
                    "links": [
                        1,
                        2
                    ],
                    "slot_index": 0
                }
            ],
            "title": "A",
            "properties": {
                "name": "A",
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
                "session_token": ""
            },
            "widgets_values": [
                "You are an AI assistant using the following passages to answer the user questions on policies at the UKHO (UK Hydrogrpahic Office). You should also use the content in any of the links in the passages as SOURCES. Each passage has a NAME which is the title of the document. After your answer, leave a blank line and then give the source html link(s) of the passages you answered from. Put them in a <br> separated list, prefixed with SOURCES and do not adjust the embedded html data in the source links:.",
                [
                    "Example: Question: What is the meaning of life? Response: The meaning of life is 42. SOURCES: <a href='https://some/web/reference>'>Hitchhiker's Guide to the Galaxy</a>"
                ],
                "a question about a UKHO policy",
                "a detailed and specific job posting ",
                [],
                [],
                "default",
                "default"
            ]
        },
        {
            "id": 5,
            "type": "roles/test_role",
            "pos": {
                "0": 487,
                "1": 125,
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
            "order": 1,
            "mode": 0,
            "inputs": [
                {
                    "name": "Input Request",
                    "type": "text",
                    "link": 1
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
                    "links": [
                        4
                    ],
                    "slot_index": 0
                }
            ],
            "title": "B",
            "properties": {
                "name": "B",
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
                "session_token": ""
            },
            "widgets_values": [
                "You are an AI assistant using the following passages to answer the user questions on policies at the UKHO (UK Hydrogrpahic Office). You should also use the content in any of the links in the passages as SOURCES. Each passage has a NAME which is the title of the document. After your answer, leave a blank line and then give the source html link(s) of the passages you answered from. Put them in a <br> separated list, prefixed with SOURCES and do not adjust the embedded html data in the source links:.",
                [
                    "Example: Question: What is the meaning of life? Response: The meaning of life is 42. SOURCES: <a href='https://some/web/reference>'>Hitchhiker's Guide to the Galaxy</a>"
                ],
                "a question about a UKHO policy",
                "a detailed and specific job posting ",
                [],
                [],
                "default",
                "default"
            ]
        },
        {
            "id": 7,
            "type": "roles/test_role",
            "pos": {
                "0": 933,
                "1": 559,
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
            "order": 4,
            "mode": 0,
            "inputs": [
                {
                    "name": "Input Request",
                    "type": "text",
                    "link": 6
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
            "title": "D",
            "properties": {
                "name": "D",
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
                "session_token": ""
            },
            "widgets_values": [
                "You are an AI assistant using the following passages to answer the user questions on policies at the UKHO (UK Hydrogrpahic Office). You should also use the content in any of the links in the passages as SOURCES. Each passage has a NAME which is the title of the document. After your answer, leave a blank line and then give the source html link(s) of the passages you answered from. Put them in a <br> separated list, prefixed with SOURCES and do not adjust the embedded html data in the source links:.",
                [
                    "Example: Question: What is the meaning of life? Response: The meaning of life is 42. SOURCES: <a href='https://some/web/reference>'>Hitchhiker's Guide to the Galaxy</a>"
                ],
                "a question about a UKHO policy",
                "a detailed and specific job posting ",
                [],
                [],
                "default",
                "default"
            ]
        },
        {
            "id": 6,
            "type": "roles/test_role",
            "pos": {
                "0": 342,
                "1": 681,
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
                    "links": [
                        6,
                        7
                    ],
                    "slot_index": 0
                }
            ],
            "title": "C",
            "properties": {
                "name": "C",
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
                "session_token": ""
            },
            "widgets_values": [
                "You are an AI assistant using the following passages to answer the user questions on policies at the UKHO (UK Hydrogrpahic Office). You should also use the content in any of the links in the passages as SOURCES. Each passage has a NAME which is the title of the document. After your answer, leave a blank line and then give the source html link(s) of the passages you answered from. Put them in a <br> separated list, prefixed with SOURCES and do not adjust the embedded html data in the source links:.",
                [
                    "Example: Question: What is the meaning of life? Response: The meaning of life is 42. SOURCES: <a href='https://some/web/reference>'>Hitchhiker's Guide to the Galaxy</a>"
                ],
                "a question about a UKHO policy",
                "a detailed and specific job posting ",
                [],
                [],
                "default",
                "default"
            ]
        },
        {
            "id": 9,
            "type": "roles/test_role",
            "pos": {
                "0": 934,
                "1": 986,
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
            "order": 5,
            "mode": 0,
            "inputs": [
                {
                    "name": "Input Request",
                    "type": "text",
                    "link": 7
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
            "title": "F",
            "properties": {
                "name": "F",
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
                "session_token": ""
            },
            "widgets_values": [
                "You are an AI assistant using the following passages to answer the user questions on policies at the UKHO (UK Hydrogrpahic Office). You should also use the content in any of the links in the passages as SOURCES. Each passage has a NAME which is the title of the document. After your answer, leave a blank line and then give the source html link(s) of the passages you answered from. Put them in a <br> separated list, prefixed with SOURCES and do not adjust the embedded html data in the source links:.",
                [
                    "Example: Question: What is the meaning of life? Response: The meaning of life is 42. SOURCES: <a href='https://some/web/reference>'>Hitchhiker's Guide to the Galaxy</a>"
                ],
                "a question about a UKHO policy",
                "a detailed and specific job posting ",
                [],
                [],
                "default",
                "default"
            ]
        }
    ],
    "links": [
        [
            1,
            4,
            0,
            5,
            0,
            "text"
        ],
        [
            2,
            4,
            0,
            6,
            0,
            "text"
        ],
        [
            4,
            5,
            0,
            8,
            0,
            "text"
        ],
        [
            6,
            6,
            0,
            7,
            0,
            "text"
        ],
        [
            7,
            6,
            0,
            9,
            0,
            "text"
        ]
    ],
    "groups": [],
    "config": {},
    "extra": {},
    "version": 0.4,
    "name": "flow_sort_test",
    "level": "user",
    "id": "flow_sort_test",
    "ttl": -1,
    "data_type": "flows",
    "tenant": "ukho",
    "user_id": "12345",
    "_rid": "OT16ALmnWS6QCwAAAAAAAA==",
    "_self": "dbs/OT16AA==/colls/OT16ALmnWS4=/docs/OT16ALmnWS6QCwAAAAAAAA==/",
    "_etag": "\"4f016798-0000-1000-0000-665f3d0d0000\"",
    "_attachments": "attachments/",
    "_ts": 1717517581
}

order = flow.topological_sort(flow1)

# A = 4
# B = 5
# C = 6
# D = 7
# E = 8
# F = 9
# A -> B -> E
#   -> C -> D
#        -> F
# Order should be:
# 4, [5,6], [7,8,9]
print("Nodes in order of execution:", [item["id"] for item in order])



found = flow.find_nodes(flow1)

print(f"Found input nodes: {found}")
