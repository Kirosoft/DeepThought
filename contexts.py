
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
    agent_config = AgentConfig(body, user_settings_keys=user_settings["keys"]) if body != '' else AgentConfig(user_settings_keys=user_settings["keys"])
    operation_type = req.method
    item_id = req.params.get("id") if req.params is not None else None

    try:
        # optional setting overrides when called as a tool
        json_body = json.loads(body)
        operation_type = json_body['operation'] if json_body is not None and "operation" in json_body else operation_type
        item_id = json_body['id'] if 'id' in json_body else item_id
    except Exception as err:
        logging.debug(f"Debug Warning: optional payload overrides: {err}")

    match operation_type:
        case "POST" | "create" | "update":
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
        case "DELETE" | "delete":
            try:
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
        case "GET" | "list" | "list_all":
            try:
                context = Context(agent_config, user_settings["user_id"], user_settings["user_tenant"])
                if item_id is not None and item_id != '':
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
        case default:
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

    item_id = req.params.get("id") if req.params is not None else None

    try:
        # optional setting overrides when called as a tool
        body = req.get_body().decode('utf-8')
        json_body = json.loads(body)
        item_id = json_body['id'] if 'id' in json_body else item_id
    except Exception as err:
        logging.debug(f"Debug Warning: optional payload overrides: {err}")

    input = {
        "user_settings":user_settings,
        "id":item_id
    }

    instance_id = await client.start_new("orchestrate_context", None, input )
    logging.info(f"Started orchestration with ID = '{instance_id}'.")

    return client.create_check_status_response(req, instance_id)


@df_contexts.orchestration_trigger(context_name="context")
def orchestrate_context(context: df.DurableOrchestrationContext):
    input_data = context.get_input()  # Retrieve input data

    docs = yield context.call_activity('run_loader', input_data)
    # result2 = yield context.call_activity('run_adaptor', "2")
    # result3 = yield context.call_activity('do_chunk', "3")
    # result4 = yield context.call_activity('do_encode', "4")
    

    return [docs]


@df_contexts.activity_trigger(input_name="inputdata")
def run_loader(inputdata):

    user_settings = inputdata["user_settings"]
    agent_config = AgentConfig(user_settings_keys=user_settings["keys"])

    context_crud = Context(agent_config, user_settings["user_id"], user_settings["user_tenant"])
    context = context_crud.get_context(inputdata["id"])
    loader = Loader(agent_config, user_settings["user_id"], user_settings["tenant"])

    docs = loader.run(context["loader"], context["loader_args"])
    if docs != None and len(docs) > 0:
        next_version = context["current_version"]+1

        result = context_crud.process_content(docs, context["id"], next_version)

        # move the current version
        context["current_version"] = next_version

        #schedule last version for deletion
        if next_version > 1:
            context_crud.schedule_for_deletion(context['id'], next_version-1, 60*1)

        context_crud.save_context(context)

        # You can access the input with context.get_input() if needed
        return result
    return ""

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


@df_contexts.activity_trigger(input_name="name")
def save_context(name: str) -> str:
    # You can access the input with context.get_input() if needed
    return f"do import: {name}"


