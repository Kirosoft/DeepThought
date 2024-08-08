
import azure.functions as func
import logging
from core.security.security_utils import validate_request
import json
from core.agent.agent_config import AgentConfig
from core.middleware.function_definition import FunctionDefinition

function = func.Blueprint()

@function.function_name(name="functions_crud")
@function.route(auth_level=func.AuthLevel.ANONYMOUS)
def functions_crud(req: func.HttpRequest) -> func.HttpResponse:  

    logging.info('functions CRUD')

    response = validate_request(req)
    if type(response) is func.HttpResponse:
        return response
    else:
        response_headers = response["response_headers"]
        user_settings = response["user_settings"]
        payload = response["payload"]
    
    body = req.get_body().decode('utf-8')
    agent_config = AgentConfig(body, user_settings_keys=user_settings["keys"]) if body != '' else AgentConfig(user_settings_keys=user_settings["keys"])

    if req.method == "POST":
        try:
            json_body = json.loads(body)
            function_definition = FunctionDefinition(agent_config, user_settings["user_id"], user_settings["user_tenant"])
            result = function_definition.save_function_definition(json_body)
            response_str = json.dumps(result, ensure_ascii=False).encode('utf8')
            return func.HttpResponse(response_str, headers=response_headers, status_code=200)
        except ValueError:
            return func.HttpResponse(
                "Invalid JSON",
                status_code=400,
                headers=response_headers
            )
    if req.method == "DELETE":
        try:
            item_id = req.params.get('id')
            function_definition = FunctionDefinition(agent_config, user_settings["user_id"], user_settings["user_tenant"])
            result = function_definition.delete_function_definition(item_id)
            response_str = json.dumps(result, ensure_ascii=False).encode('utf8')
            return func.HttpResponse(response_str, headers=response_headers, status_code=200)
        except ValueError:
            return func.HttpResponse(
                "Invalid JSON",
                status_code=400,
                headers=response_headers
            )
    elif req.method == "GET":
        try:
            item_id = req.params.get('id')
            function_definition = FunctionDefinition(agent_config, user_settings["user_id"], user_settings["user_tenant"])
            if item_id is not None:
                result = function_definition.get_function_definition(item_id)
            else:
                result = function_definition.get_function_definitions()

            logging.info('Loaded functions')
            response_str = json.dumps(result, ensure_ascii=False).encode('utf8')
            return func.HttpResponse(response_str, headers=response_headers, status_code=200)
        except ValueError:
            return func.HttpResponse(
                "Invalid JSON",
                status_code=400,
                headers=response_headers
            )
    else:
        return func.HttpResponse("Method not allowed", status_code=405, headers=response_headers)
