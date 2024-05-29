
import azure.functions as func
import azure.durable_functions as df

import logging
from core.security.security_utils import validate_request
import json
from core.agent.agent_config import AgentConfig
from core.middleware.context import Context
from core.middleware.loader import Loader

contexts = func.Blueprint()
df_contexts  = df.Blueprint()


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

@df_contexts.route(route="run_context")
@df_contexts.durable_client_input(client_name="client")
async def run_context(req: func.HttpRequest, client) -> func.HttpResponse:  

    logging.info('run context')

    response = validate_request(req)
    if type(response) is func.HttpResponse:
        return response
    else:
        response_headers = response["response_headers"]
        user_settings = response["user_settings"]
        payload = response["payload"]

    body = req.get_body().decode('utf-8')

    instance_id = await client.start_new("orchestrate_context", None, body)
    monitoring_url = client.create_http_management_payload(instance_id)

    return func.HttpResponse(body=monitoring_url, status_code=202, headers=response_headers)


@df_contexts.orchestration_trigger(context_name="context")
async def orchestrate_context(context):
    input_data = context.get_input()  # Retrieve input data

    # You can process or pass this data to activity functions as needed
    # TODO: migrate version
    result1 = await context.call_activity('run_loader', input_data)
    result2 = await context.call_activity('run_adaptor', input_data)
    result3 = await context.call_activity('run_embedding', input_data)
    result4 = await context.call_activity('do_import', input_data)
    
    return [result1, result2, result3, result4]


@df_contexts.activity_trigger
def run_loader(name: str) -> str:
    # You can access the input with context.get_input() if needed
    return f"run loader: {name}"

@df_contexts.activity_trigger
def run_adaptor(name: str) -> str:
    # You can access the input with context.get_input() if needed
    return f"run adaptor: {name}"


@df_contexts.activity_trigger
def run_embedding(name: str) -> str:
    # You can access the input with context.get_input() if needed
    return f"run embedding: {name}"

@df_contexts.activity_trigger
def do_import(name: str) -> str:
    # You can access the input with context.get_input() if needed
    return f"do import: {name}"



