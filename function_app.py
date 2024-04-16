import azure.functions as func
import logging
import datetime
import json

# Local 
from core.agent.agent_llm import AgentLLM
from core.agent.agent_role import AgentRole
from core.agent.agent_config import AgentConfig
from core.agent.agent_memory import AgentMemory

app = func.FunctionApp()

#@app.event_hub_message_trigger(arg_name="azeventhub", event_hub_name="deepthoughtcore",connection="DeepThoughtEvents_RootManageSharedAccessKey_EVENTHUB") 
#@app.event_hub_output(arg_name="answer",event_hub_name="deepthoughtoutput", connection="DeepThoughtEvents_RootManageSharedAccessKey_EVENTHUB")

@app.function_name(name="core_llm_agent")
@app.route(auth_level=func.AuthLevel.ANONYMOUS)
def core_llm_agent(req: func.HttpRequest) -> func.HttpResponse:  # , answer: func.Out[str]

    logging.info('core_llm_agent trigger from event hub input')

    agent_config = AgentConfig(req.get_body())
     
    if agent_config.is_valid():
        logging.info('core_llm_agent processed an event: %s',agent_config.input)
        agent_memory = AgentMemory(agent_config)
        agent_role = AgentRole(agent_config)
        agent_llm = AgentLLM(agent_config)

        # retrieve any context results
        context_results = agent_memory.get_context(agent_config.input) if agent_role.use_context_search(agent_config.role) else ""

        # retrieve any session history
        session_history = agent_memory.get_session_history(agent_config.session_token) if agent_role.use_session_history(agent_config.role) else []

        # use the configured role to find the prompt and populate with the context and session history as required
        completed_prompt, tools, routing = agent_role.get_completed_prompt(context_results, session_history, agent_config.role)

        llm_result = agent_llm.run_inference(completed_prompt, agent_config.input, agent_config.role, tools, routing)

        # TODO: should we execute tool
        # 1) push the tool execute to the Q
        # 2) Push the response to the Q
        logging.info(f'Answer: {llm_result["answer"]} - session {llm_result["session_token"]}')
        #answer.set('test')
        func.HttpResponse(llm_result["answer"])
    else:
        answer_str = 'No question found, please supply a question'
        logging.info('Answer: %s',answer_str)
        func.HttpResponse(answer_str)
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
