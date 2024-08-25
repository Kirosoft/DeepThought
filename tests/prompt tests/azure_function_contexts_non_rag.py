import os
from core.db.agent_db_base import AgentDBBase
from core.agent.agent_config import AgentConfig
import json
from langchain_community.document_loaders import TextLoader
from os.path import join
import logging
import urllib3
import requests

from  core.utils.schema import create_dynamic_model

urllib3.disable_warnings()

base_url = "http://localhost:7071/api"
#base_url = "https://deepthought-app.azurewebsites.net/api"

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

# quick schema test

policy = {
    "name": "ukho_policy",
    "description": "You are an AI assistant using the following passages to answer the user questions on policies and software coding standards at the UKHO (UK Hydrogrpahic Office). ",
    "role": "You should also use the content in any of the links in the passages as SOURCES. Each passage has a NAME which is the title of the document. After your answer, leave a blank line and then give the source html link(s) of the passages you answered from. Put them in a <br> separated list, prefixed with SOURCES and do not adjust the embedded html data in the source links:.",
    "expected_input": "a question about a UKHO software engineering policy or coding standard",
    "expected_output": "a detailed and specific job posting ",
    "output_format": [],
    "examples": [
        "Example: Question: What is the meaning of life? Response: The meaning of life is 42. SOURCES: <a href='https://some/web/reference>'>Hitchhiker's Guide to the Galaxy</a>"
    ],
    "options": {
        "rag_mode": True,
        "context": "github1",
        "icl_mode": True,
        "icl_context": "icl_test",
		"prefetch_tool_mode":True,
		"prefetch_role_mode":True,
		"prefetch_context_mode":True,
        "model_override":"groq:llama-3.1-405b-reasoning",
        "role_override":True,
        "role_override_context":"deepthoughtai",
        "use_structured_output":True,
        "use_reasoning":True
    },
    "level":"user"
}


SchemaModel = create_dynamic_model(policy)
schema_model = SchemaModel.schema()
#print(schema_model)



### Test Auth ####
headers = {
    'Content-Type': 'application/json',
    'x-user-id': 'ukho',
    'x-password': 'my_password'
    }

url = f"{base_url}/request_auth"
response = requests.get(url, headers=headers)

token = json.loads(response.content.decode('utf-8'))

### Create the a github reader for .role and .schema files ####
url = f"{base_url}/contexts_crud"
new_context = {
    "id": "deepthoughtai",
    "name": "deepthoughtai",
    "loader": "github_file_loader",
    "loader_args": {
        "repo": "Kirosoft/DeepThought",
        "access_token": "$GITHUB_ACCESS_TOKEN",
        "filter": [
            ".role",".schema",".function"
        ],
        "api_url": "https://api.github.com",
        "current_version": 3,
    },
    "options": {},
    "adaptor": "html_to_text",
    "adaptor_args": {},
    "level": "user"
}


headers = {
    'Authorization': f'Bearer {token["token"]}',
    'Content-Type': 'application/json',
    'x-user-id': 'ukho'
    }

params = {'id': new_context["id"]}

# create a new context
# payload = json.dumps(new_context, ensure_ascii=False).encode('utf8')
# response = requests.post(url, payload, headers=headers)
# response_json = response.json()
# print(response_json)

# get the new context
response = requests.get(url, params=params, headers=headers)
response_json = response.json()
print(response_json)


#run the loader
# url = f"{base_url}/run_context"
# response = requests.get(url, params=params, headers=headers)
# response_json = response.json()
# print(response_json)

# create a function definition
function_definition = \
{
        "name": "run_agent",
        "schema": "function definition goes here",
        "options": {
            "schema_override":True,
            "schema_override_context":"deepthoughtai"
        }
}

# url = f"{base_url}/functions_crud"
# payload = json.dumps(function_definition, ensure_ascii=False).encode('utf8')
# response = requests.post(url, payload, headers=headers)
# response_json = response.json()
# print(response_json)

#test - a prompt using 'auto' role mode
document = {"input": "I would like to create a new role called quiz_master, this should generate 10 new pub quiz questions on a variety of topics. The topics will be provided via a new context","role":"auto", "name":"run_agent"}

headers = {
    'Authorization': f'Bearer {token["token"]}',
    'Content-Type': 'application/json',
    'x-user-id': 'ukho'
    }
payload = json.dumps(document, ensure_ascii=False).encode('utf8')

print("----------------------------------------------------------------------------------------------------------------------------")
url = f"{base_url}/run_agent"
response = requests.post(url, payload, headers=headers)
response_json = response.json()
print(response_json)

finished = False

while not finished:
    print("----------------------------------------------------------------------------------------------------------------------------")
    match response_json["answer_type"]:
        case "user_input_needed":
            print(f"ANSWER: {response_json['answer']}")
            
            user_input = input("> ")
            document = {"input": user_input,"role":response_json["role"],"parent_role":response_json["parent_role"], "name":"run_agent", "session_token":response_json["session_token"]}
            payload = json.dumps(document, ensure_ascii=False).encode('utf8')
            url = f"{base_url}/run_agent"
            response = requests.post(url, payload, headers=headers)
            response_json = response.json()
            #print(response_json)
            
        case "tool_calls":
            url = f"{base_url}/{response_json['tool_name']}"
            tool_arguments = json.loads(json.loads(response_json["tool_arguments"]))
            tool_id=response_json['id']

            if response_json['tool_name'] == "run_agent":
                #### running agent ####
                tool_arguments["session_token"] = response_json["session_token"]
                # move current call into the parent stack
                tool_arguments["parent_role"].push({"role":response_json["role"], "id":response_json["answer"]["tool_calls"][0]["id"]}) 
                tool_arguments["role"] = tool_arguments["role"].split("//")[1] if "//" in tool_arguments["role"] else tool_arguments["role"]
                print(f"Contacting agent: {tool_arguments['role']} {tool_id} with input: {tool_arguments['input']} -  session token: {response_json['session_token']}")
                payload = json.dumps(tool_arguments, ensure_ascii=False).encode('utf8')
                response = requests.post(url, payload, headers=headers)
                response_json = response.json()
                #print(response_json)
            else:
                # run the tool
                print(f"running tool: tool:{response_json['tool_name']}[{tool_id}] with input: {json.dumps(tool_arguments)} -  session token: {response_json['session_token']}")
                payload = json.dumps(tool_arguments, ensure_ascii=False).encode('utf8')
                tool_response = requests.post(url, payload, headers=headers)
                tool_response_json = tool_response.json()
                #print(tool_response_json)
                if tool_response.status_code == 200:
                    # the tool call succeeded
                    message = f"operation {tool_arguments['operation']} {response_json['tool_name']} succeeded"
                    function_response = {
                        "role":"tool",
                        "content":message,
                        "tool_call_id":response_json["answer"]["tool_calls"][0]["id"]
                    }
                    arguments = {"input":function_response, "name":"run_agent", "role":response_json["role"], "session_token":response_json["session_token"]}
                    print(f"Sending tool response to agent {response_json['role']}: {response_json['tool_name']} with answer: {input} -  session token: {response_json['session_token']}")

                    document = {"input": arguments,"role":response_json["role"],"parent_role":response_json["parent_role"], "name":"run_agent", "session_token":response_json["session_token"]}
                    payload = json.dumps(document, ensure_ascii=False).encode('utf8')
                    url = f"{base_url}/run_agent"
                    response = requests.post(url, payload, headers=headers)
                    response_json = response.json()
                    # TODO: make sure we respond like the tool call was successfull
                    #print(response_json)
                else:
                    print("Something went wrong")

        case "completed":
            finished = True

        case "error":
            finished = True
        case default:
            # pop the parent role
            role = response_json["parent_role"].pop()
            # respond back with the correct tool id

            finished = True



