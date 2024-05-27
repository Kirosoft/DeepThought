
import azure.functions as func
import logging
from core.security.security_utils import validate_request
import json
from core.agent.agent_config import AgentConfig
from core.middleware.context import Context
from core.middleware.loader import Loader

contexts = func.Blueprint()

@contexts.function_name(name="contexts_crud")
@contexts.route(auth_level=func.AuthLevel.ANONYMOUS)
def contexts_crud(req: func.HttpRequest) -> func.HttpResponse:  

    logging.info('contexts CRUD')

    response = validate_request(req)
    if type(response) is func.HttpResponse:
        return response
    else:
        response_headers = response["response_headers"]
        user_settings = response["user_settings"]
        payload = response["payload"]
    
    body = req.get_body().decode('utf-8')
    agent_config = AgentConfig(body) if body != '' else AgentConfig()

    if req.method == "POST":
        try:
            json_body = json.loads(body)
            context = Context(agent_config, user_settings["user_id"], user_settings["user_tenant"])
            result = context.save_context(json_body)
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
            context = Context(agent_config, user_settings["user_id"], user_settings["user_tenant"])
            result = context.delete_context(item_id)
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
            context = Context(agent_config, user_settings["user_id"], user_settings["user_tenant"])
            if item_id is not None:
                result = context.get_context(item_id)
            else:
                result = context.load_all_contexts()

            logging.info('Loaded contexts')
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


@contexts.function_name(name="run_context")
@contexts.route(auth_level=func.AuthLevel.ANONYMOUS)
def run_context(req: func.HttpRequest) -> func.HttpResponse:  

    logging.info('run context')

    response = validate_request(req)
    if type(response) is func.HttpResponse:
        return response
    else:
        response_headers = response["response_headers"]
        user_settings = response["user_settings"]
        payload = response["payload"]

    # find the loader in the context
    body = req.get_body().decode('utf-8')
    agent_config = AgentConfig(body) if body != '' else AgentConfig()

    loader = Loader(agent_config, user_settings["user_id"], user_settings["user_tenant"])
    loaderArgs = body["LoaderArgs"]

    docLoader = loader.get(body["loaderName"])
    