import os
from core.db.agent_db_base import AgentDBBase
from core.agent.agent_config import AgentConfig
import json
from langchain_community.document_loaders import TextLoader
from os.path import join
import logging
import urllib3
import requests

urllib3.disable_warnings()

base_url = "http://localhost:7071/api"
#base_url = "https://deepthought-app.azurewebsites.net/api"

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

token = None

def get_header_auth():

    ### Test Auth ####
    headers = {
        'Content-Type': 'application/json',
        'x-user-id': 'ukho',
        'x-password': 'my_password'
        }

    url = f"{base_url}/request_auth"
    response = requests.get(url, headers=headers)

    token = json.loads(response.content.decode('utf-8'))

    return token

def function_response(message, id):
    return  {"input":{
        "role":"tool",
        "content":message,
        "tool_call_id":id
    }}

def run_tool(document, tool_name="run_agent"):
    global token

    if token is None:
        token = get_header_auth()

    headers = {
        'Authorization': f'Bearer {token["token"]}',
        'Content-Type': 'application/json',
        'x-user-id': 'ukho'
        }
    payload = json.dumps(document, ensure_ascii=False).encode('utf8')

    print("----------------------------------------------------------------------------------------------------------------------------")
    url = f"{base_url}/{tool_name}"

    operation = document["operation"] if "operation" in document else "default"

    match operation:
        case "update" | "create" | "default":
            response = requests.post(url, payload, headers=headers)
        case "list" | "list_all":
            response = requests.get(url, payload, headers=headers)
        case "delete":
            response = requests.delete(url, payload, headers=headers)
        case default:
            response = requests.post(url, payload, headers=headers)

    if response.status_code == 200:
        response_json = response.json()

        if tool_name != 'run_agent':
            ################ Send the tool response ##################
            document = {"input": function_response(f"{tool_name} succeeded - response: {response_json}", document["call_id"]),
                        "role":document["role"],"parent_role":document["parent_role"], "name":"run_agent", "session_token":document["session_token"]}
            response_json = run_agent(document)

        print(response_json["answer"] if response_json["answer_type"] != "done" else "Done") 

        handle_agent_response(response_json)
        return {"answer_type":"done"}
    else:
        return {"answer_type":response["reason"]}

def run_agent(document):
    return run_tool(document, "run_agent")

def handle_complete(response_json):
    # pop the parent role
    next_role = response_json["parent_role"].pop() if len(response_json["parent_role"]) > 0 else None
    # respond back with the correct tool id
    if next_role is not None:
        message = f"operation run_agent {response_json['role']} succeeded"
        document = {"input": function_response(message, next_role['id']),"role":next_role["role"],"parent_role":response_json["parent_role"], "name":"run_agent", "session_token":response_json["session_token"]}
        response_json = run_agent(document)
    else:
        print("all done")
        response_json = {"answer_type":"done"}

    return response_json

def handle_tool_call(response_json):
    tool_arguments = json.loads(json.loads(response_json["tool_arguments"]))
    tool_arguments["session_token"] = response_json["session_token"]
    tool_arguments["parent_role"] = response_json['parent_role']

    call_id = response_json["answer"]["tool_calls"][0]["id"]
    tool_arguments["call_id"] = call_id

    if response_json['tool_name'] == "run_agent":
        #### running agent ####
        # move current call into the parent stack
        tool_arguments["role"] = tool_arguments["role"].split("//")[1] if "//" in tool_arguments["role"] else tool_arguments["role"]
        tool_arguments["parent_role"].append({"role":response_json["role"], "id":call_id}) 

        response_json = run_agent(tool_arguments)
    else:
        # run the tool
        tool_arguments["role"] = response_json['role']
        response_json = run_tool(tool_arguments, response_json['tool_name'])

    return response_json

def handle_agent_response(response_json):
    finished = False

    while not finished:
        match response_json["answer_type"]:
            case "user_input_needed":
                print(f"ANSWER: {response_json['answer']}")
                
                user_input = input("> ")
                document = {"input": user_input,"role":response_json["role"],"parent_role":response_json["parent_role"], "name":"run_agent", "session_token":response_json["session_token"]}
                response_json = run_agent(document)
                
            case "tool_calls":
                response_json = handle_tool_call(response_json)

            case "complete":
                response_json = handle_complete(response_json)

            case "done":
                finished = True

            case "error":
                print("OK that went wrong")
                finished = True
            case default:
                print("Unexpected item in the bagging area")
                finished = True

# Main Execution
if __name__ == "__main__":
    # test input
    document = {"input": "I would like to create a new role called quiz_master, this should generate 10 new pub quiz questions on a variety of topics. The topics will be provided via a new context","role":"auto", "name":"run_agent"}
    user_input = "quiz_topics is the id and name, the data will come from github repo: https://github.com/Kirosoft/DeepThoughtData - look for files ending .quiz, use standard rag options"
    finished = False

    while not finished:
        user_input = input(">> ")

        if (user_input == "quit" or user_input=="exit"):
            finished = True
        else:
            document = {"input": user_input,"role":"auto", "name":"run_agent"}
            run_agent(document)

    print("Exit")
