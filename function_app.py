import azure.functions as func
import azure.durable_functions as df
import logging

from tools import tools
from security import security
from agent import agent
from roles import roles
from flows import flows, df_flows
from contexts import contexts, df_contexts

import urllib3

urllib3.disable_warnings()

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

app.register_functions(tools) 
app.register_functions(security) 
app.register_functions(agent)
app.register_functions(roles)
app.register_functions(flows)
app.register_functions(contexts)

app.register_functions(df_contexts)
app.register_functions(df_flows)

# activity functions


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
