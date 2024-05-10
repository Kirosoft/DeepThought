import azure.functions as func
import logging
import json
from core import process_request, get_user_context, RateLimitError, CreditBalanceError, create_jwt 
import urllib3
from context import do_import
import jwt
import os

urllib3.disable_warnings()

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

app = func.FunctionApp()

response_headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': 'null',  # Disallow any origin not in allowed_origins
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
}
@app.function_name(name="core_llm_agent")
@app.route(auth_level=func.AuthLevel.ANONYMOUS)
def core_llm_agent(req: func.HttpRequest) -> func.HttpResponse:  

    logging.info('core_llm_agent trigger from http')

    # Handle preflight requests
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=response_headers)

    auth_header = req.headers.get('Authorization')
    if not auth_header:
        return func.HttpResponse("Authorization header is missing", status_code=401)

    user_id = req.headers.get('x-user-id')  # Assume user ID is passed in header for simplicity
    if not user_id:
        return func.HttpResponse("User ID is required", status_code=400)
    
    try:
        user_settings = get_user_context(user_id)
    except RateLimitError as e:
        return func.HttpResponse("Rate limit exceeded", status_code=429)
    except CreditLimitError as e:
        return func.HttpResponse("Credit limit balance is zero", status_code=429)

    # Get the request origin
    request_origin = req.headers.get('Origin')
    if request_origin in user_settings["origins"]:
        response_headers['Access-Control-Allow-Origin'] = request_origin,  # Echo the origin back

    auth_header = req.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return func.HttpResponse("Unauthorized: No token provided", status_code=401, headers=response_headers)

    token = auth_header.split(' ')[1]
    try:
        # Decode and validate JWT
        # Adjust 'algorithms' based on your JWT's signing algorithm
    
        payload = jwt.decode(token, user_settings["secret_key"], algorithms=["HS256"])
        # TODO: cross validate the headeruserid with the decrypted userid

    except jwt.ExpiredSignatureError:
        return func.HttpResponse("Token expired", status_code=401, headers=response_headers)
    except jwt.InvalidTokenError:
        return func.HttpResponse("Invalid token", status_code=401, headers=response_headers)

    if req.method == "POST":
        try:
            result = process_request(req.get_body().decode('utf-8'), user_settings["tenant"], user_settings["user_id"])

            if (result != None):
                logging.info('Answer: %s',result["answer"])
                response_str = json.dumps(result, ensure_ascii=False).encode('utf8')
                return func.HttpResponse(response_str, headers=response_headers, status_code=200)
            else:
                answer_str = {"answer":"No question found, please supply a question", "answer_type":"error"}
                logging.info('Answer: %s',answer_str)

                return func.HttpResponse(
                    answer_str,
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

    # Handle preflight requests
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=response_headers)

    user_id = req.headers.get('x-user-id')  # Assume user ID is passed in header for simplicity
    if not user_id:
        return func.HttpResponse("User ID is required", status_code=400)

    try:
        user_settings = get_user_context(user_id)
    except RateLimitError as e:
        return func.HttpResponse("Rate limit exceeded", status_code=429)
    except CreditBalanceError as e:
        return func.HttpResponse("Credit limit balance is zero", status_code=429)

    # Get the request origin
    request_origin = req.headers.get('Origin')
    if request_origin in user_settings["origins"]:
        response_headers['Access-Control-Allow-Origin'] = request_origin,  # Echo the origin back

    password = req.headers.get('x-password') 
    if not password:
        return func.HttpResponse("password header is required", status_code=400)
    elif password != user_settings["password"]:
        return func.HttpResponse("account credentials do not match", status_code=400)

    # create token
    token = create_jwt(user_id, user_settings["secret_key"])

    return func.HttpResponse(token, headers=response_headers, status_code=200)
    

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
