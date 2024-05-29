
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

    #body = req.get_body().decode('utf-8')

    input = {
        "user_settings":user_settings,
        "id":req.params.get("id","")
    }

    instance_id = await client.start_new("orchestrate_context", None, input )
    logging.info(f"Started orchestration with ID = '{instance_id}'.")

    return client.create_check_status_response(req, instance_id)


@df_contexts.orchestration_trigger(context_name="context")
def orchestrate_context(context: df.DurableOrchestrationContext):
    input_data = context.get_input()  # Retrieve input data
    user_settings = input_data["user_settings"]

    # You can process or pass this data to activity functions as needed
    # TODO: migrate version
    agent_config = AgentConfig(user_settings_keys=user_settings["keys"])
    context_crud = Context(agent_config, user_settings["user_id"], user_settings["user_tenant"])

    context_definition = context_crud.get_context(input_data["id"])
    context_definition["user_settings_keys"] = user_settings["keys"]

    result1 = yield context.call_activity('run_loader', context_definition)
    # result2 = yield context.call_activity('run_adaptor', "2")
    # result3 = yield context.call_activity('run_embedding', "3")
    # result4 = yield context.call_activity('do_import', "4")
    
    return [result1]


@df_contexts.activity_trigger(input_name="name")
def run_loader(name):

    loader = Loader(AgentConfig(), name["user_id"], name["tenant"])
    result = loader.run(name["loader"], name["loader_args"])

    # You can access the input with context.get_input() if needed
    return f"run loader: "

@df_contexts.activity_trigger(input_name="name")
def run_adaptor(name: str) -> str:
    # You can access the input with context.get_input() if needed
    return f"run adaptor: {name}"


@df_contexts.activity_trigger(input_name="name")
def run_embedding(name: str) -> str:
    # You can access the input with context.get_input() if needed
    return f"run embedding: {name}"

@df_contexts.activity_trigger(input_name="name")
def do_import(name: str) -> str:
    # You can access the input with context.get_input() if needed
    return f"do import: {name}"



