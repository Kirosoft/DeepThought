# Register this blueprint by adding the following line of code 
# to your entry point file.  
# app.register_functions(tools) 
# 
# Please refer to https://aka.ms/azure-functions-python-blueprints


import azure.functions as func
import logging
from core.security.security_utils import validate_request
from core.agent.agent_config import AgentConfig

tools = func.Blueprint()


@tools.route(route="rag_tool", auth_level=func.AuthLevel.FUNCTION)
def rag_tool(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')


    logging.info('tools CRUD')

    response = validate_request(req)
    if type(response) is func.HttpResponse:
        return response
    else:
        response_headers = response["response_headers"]
        user_settings = response["user_settings"]
        payload = response["payload"]
    
    body = req.get_body().decode('utf-8')
    agent_config = AgentConfig(body) if body != '' else AgentConfig()

