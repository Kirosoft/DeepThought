import azure.functions as func
import logging
import json
from core.agent.agent_role import AgentRole
from core.agent.agent_config import AgentConfig
from core.security.security_utils import validate_request, create_jwt
from core.middleware.role import Role

import urllib3

urllib3.disable_warnings()

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

app = func.FunctionApp()

@app.function_name(name="run_agent")
@app.route(auth_level=func.AuthLevel.ANONYMOUS)
def run_agent(req: func.HttpRequest) -> func.HttpResponse:  

    logging.info('core_llm_agent trigger from http')

    response = validate_request(req)
    if type(response) is func.HttpResponse:
        return response
    else:
        response_headers = response["response_headers"]
        user_settings = response["user_settings"]
        payload = response["payload"]
    
    if req.method == "POST":
        try:
            agent = AgentRole(user_settings["user_id"], user_settings["user_tenant"])
            result = agent.run_agent(req.get_body().decode('utf-8'))

            if (result != None):
                logging.info('Answer: %s',result["answer"])
                response_str = json.dumps(result, ensure_ascii=False).encode('utf8')
                return func.HttpResponse(response_str, headers=response_headers, status_code=200)
            else:
                answer_str = {"answer":"No question found, please supply a question", "answer_type":"error"}
                logging.info('Answer: %s',answer_str)
                response_str = json.dumps(answer_str, ensure_ascii=False).encode('utf8')

                return func.HttpResponse(
                    response_str,
                    status_code=200,
                    headers=response_headers
                )
        except ValueError:
            return func.HttpResponse(
                "Invalid JSON",
                status_code=400,
                headers=response_headers
            )
    else:
        return func.HttpResponse("Method not allowed", status_code=405, headers=response_headers)


@app.function_name(name="request_auth")
@app.route(auth_level=func.AuthLevel.ANONYMOUS)
def request_auth(req: func.HttpRequest) -> func.HttpResponse:  
    logging.info('request_auth')

    response = validate_request(req, True)

    if type(response) is func.HttpResponse:
        return response
    else:
        response_headers = response["response_headers"]
        user_settings = response["user_settings"]
        user_id = response["user_id"]

    # create token
    token = json.dumps({"token":create_jwt(user_id, user_settings["secret_key"])}, 
                        ensure_ascii=False).encode('utf8')

    return func.HttpResponse(token, headers=response_headers, status_code=200)
    

@app.function_name(name="load_roles")
@app.route(auth_level=func.AuthLevel.ANONYMOUS)
def load_roles(req: func.HttpRequest) -> func.HttpResponse:  

    logging.info('load roles')

    response = validate_request(req)
    if type(response) is func.HttpResponse:
        return response
    else:
        response_headers = response["response_headers"]
        user_settings = response["user_settings"]
        payload = response["payload"]
    
    if req.method == "POST":
        try:
            agent_config = AgentConfig(req.get_body().decode('utf-8'))
            role = Role(agent_config, user_settings["user_id"], user_settings["user_tenant"])
            result = role.load_all_roles()

            if (result != None):
                logging.info('Loaded roles')
                response_str = json.dumps(result, ensure_ascii=False).encode('utf8')
                return func.HttpResponse(response_str, headers=response_headers, status_code=200)
            else:
                answer_str = {"result":"nothing found"}
                logging.info('Load roles - nothing found')
                response_str = json.dumps(answer_str, ensure_ascii=False).encode('utf8')

                return func.HttpResponse(
                    response_str,
                    status_code=200,
                    headers=response_headers
                )
        except ValueError:
            return func.HttpResponse(
                "Invalid JSON",
                status_code=400,
                headers=response_headers
            )
    else:
        return func.HttpResponse("Method not allowed", status_code=405, headers=response_headers)



# @app.function_name(name="core_llm_agent")
# @app.route(auth_level=func.AuthLevel.ANONYMOUS)
# def save_role(req: func.HttpRequest) -> func.HttpResponse:  

#     logging.info('save role')

#     response = validate_request(req)

#     if response is func.HttpResponse:
#         return response
#     else:
#         response_headers = response["response_headers"]
#         user_settings = response["user_settings"]
#         payload = response["payload"]    
    
#     if req.method == "POST":
#         try:
#             result = process_request(req.get_body().decode('utf-8'), user_settings["tenant"], user_settings["user_id"])

#             if (result != None):
#                 logging.info('Answer: %s',result["answer"])
#                 response_str = json.dumps(result, ensure_ascii=False).encode('utf8')
#                 return func.HttpResponse(response_str, headers=response_headers, status_code=200)
#             else:
#                 answer_str = {"answer":"No question found, please supply a question", "answer_type":"error"}
#                 logging.info('Answer: %s',answer_str)
#                 response_str = json.dumps(answer_str, ensure_ascii=False).encode('utf8')

#                 return func.HttpResponse(
#                     response_str,
#                     status_code=200,
#                     headers=response_headers
#                 )
#         except ValueError:
#             return func.HttpResponse(
#                 "Invalid JSON",
#                 status_code=400,
#                 headers=response_headers
#             )
#     else:
#         return func.HttpResponse("Method not allowed", status_code=405, headers=response_headers)


# @app.schedule(schedule="0 0 6 * * *", arg_name="mytimer", run_on_startup=True) 
# def scheduled_imports(mytimer: func.TimerRequest):
#     logging.info('*** Scheduler **** ')
#     try:
#         do_import("https://api.github.com/repos/ukho/docs/git/trees/main?recursive=1")
#     except Exception as err:
#         logging.info(f"do_import {err}")

#     return 


# @app.event_hub_message_trigger(arg_name="azeventhub", event_hub_name="deepthoughtoutput",
#                                connection="DeepThoughtEvents_RootManageSharedAccessKey_EVENTHUB") 
# def eventhub_output(azeventhub: func.EventHubEvent):
#     try:
#         body = azeventhub.get_body().decode('utf-8')
#     except:
#         body = "Invalid"
    
#     logging.info('[OUTPUT]: %s',body)


# @app.route(route="http_trigger", auth_level=func.AuthLevel.ANONYMOUS)
# def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
#     logging.info('Python HTTP trigger function processed a request.')

#     name = req.params.get('name')
#     if not name:
#         try:
#             req_body = req.get_json()
#         except ValueError:
#             pass
#         else:
#             name = req_body.get('name')

#     if name:
#         return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
#     else:
#         return func.HttpResponse(
#              "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
#              status_code=200
#         )


# @app.queue_trigger(arg_name="azqueue", queue_name="main-queue",
#                                connection="868e5d_STORAGE") 
# def queue_trigger(azqueue: func.QueueMessage):
#     logging.info('Python Queue trigger processed a message: %s',
#                 azqueue.get_body().decode('utf-8'))


 
# @app.queue_trigger(arg_name="azqueue", queue_name="main",
#                                connection="AzureWebJobsStorage") 
# def queue_trigger(azqueue: func.QueueMessage):
#     body = azqueue.get_body().decode('utf-8')
#     logging.info('Python Queue trigger processed a message: %s', body)

#     result = process_request(body)

#     # TODO: should we execute tool
#     # 1) push the tool execute to the Q
#     # 2) Push the response to the Q
#     #answer.set('test')
#     if (result != None):
#         logging.info(f'Answer: {result["answer"]} session: {result["session_token"]}')
#     else:
#         answer_str = 'No question found, please supply a question'
#         logging.info('Answer: %s',answer_str)
