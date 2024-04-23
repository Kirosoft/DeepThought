import azure.functions as func
import logging

from core import process_request

app = func.FunctionApp()

#@app.event_hub_message_trigger(arg_name="azeventhub", event_hub_name="deepthoughtcore",connection="DeepThoughtEvents_RootManageSharedAccessKey_EVENTHUB") 
#@app.event_hub_output(arg_name="answer",event_hub_name="deepthoughtoutput", connection="DeepThoughtEvents_RootManageSharedAccessKey_EVENTHUB")

@app.function_name(name="core_llm_agent")
@app.route(auth_level=func.AuthLevel.ANONYMOUS)
def core_llm_agent(req: func.HttpRequest) -> func.HttpResponse:  # , answer: func.Out[str]

    logging.info('core_llm_agent trigger from event hub input')

    result = process_request(req.get_body.decode('utf-8'))

    if (result != None):
        # TODO: should we execute tool
        # 1) push the tool execute to the Q
        # 2) Push the response to the Q
        #answer.set('test')
        logging.info('Answer: %s',result["answer"])
    else:
        answer_str = 'No question found, please supply a question'
        logging.info('Answer: %s',answer_str)
        return func.HttpResponse(answer_str)
        #answer.set('error')
    
 
# @app.event_hub_message_trigger(arg_name="azeventhub", event_hub_name="deepthoughtoutput",
#                                connection="DeepThoughtEvents_RootManageSharedAccessKey_EVENTHUB") 
# def eventhub_output(azeventhub: func.EventHubEvent):
#     try:
#         body = azeventhub.get_body().decode('utf-8')
#     except:
#         body = "Invalid"
    
#     logging.info('[OUTPUT]: %s',body)



# @app.schedule(schedule="0 */5 * * * *", arg_name="mytimer", run_on_startup=True) 
# def test_function(mytimer: func.TimerRequest) -> None:
#     logging.info('*** TIMER FUNCTION **** ')




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


 
@app.queue_trigger(arg_name="azqueue", queue_name="main",
                               connection="AzureWebJobsStorage") 
def queue_trigger(azqueue: func.QueueMessage):
    body = azqueue.get_body().decode('utf-8')
    logging.info('Python Queue trigger processed a message: %s', body)

    result = process_request(body)

    # TODO: should we execute tool
    # 1) push the tool execute to the Q
    # 2) Push the response to the Q
    #answer.set('test')
    if (result != None):
        logging.info(f'Answer: {result["answer"]} session: {result["session_token"]}')
    else:
        answer_str = 'No question found, please supply a question'
        logging.info('Answer: %s',answer_str)
