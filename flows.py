import azure.functions as func
import azure.durable_functions as df

import logging
from core.security.security_utils import validate_request
import json
from core.agent.agent_config import AgentConfig
from core.middleware.flow import Flow

flows = func.Blueprint()
df_flows  = df.Blueprint()

@flows.function_name(name="flows_crud")
@flows.route(auth_level=func.AuthLevel.ANONYMOUS)
def flows_crud(req: func.HttpRequest) -> func.HttpResponse:  

    logging.info('flows CRUD')

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
            flow = Flow(agent_config, user_settings["user_id"], user_settings["user_tenant"])
            result = flow.save_flow(json_body)
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
            flow = Flow(agent_config, user_settings["user_id"], user_settings["user_tenant"])
            result = flow.delete_flow(item_id)
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
            flow = Flow(agent_config, user_settings["user_id"], user_settings["user_tenant"])
            if item_id is not None:
                result = flow.get_flow(item_id)
            else:
                result = flow.load_all_flows()

            logging.info('Loaded flows')
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

@df_flows.route(route="run_flow")
@df_flows.durable_client_input(client_name="client")
async def run_flow(req: func.HttpRequest, client) -> func.HttpResponse:  

    logging.info('run flow')

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

    instance_id = await client.start_new("orchestrate_flow", None, input )
    logging.info(f"Started orchestration with ID = '{instance_id}'.")

    return client.create_check_status_response(req, instance_id)


@df_flows.orchestration_trigger(context_name="context")
def orchestrate_flow(context: df.DurableOrchestrationContext):
    input_data = context.get_input()  # Retrieve input data

    docs = yield context.call_activity('execute_node', input_data)
    # result2 = yield context.call_activity('run_adaptor', "2")
    # result3 = yield context.call_activity('do_chunk', "3")
    # result4 = yield context.call_activity('do_encode', "4")
    

    return [docs]

@df_flows.activity_trigger(input_name="inputdata")
def execute_node(inputdata):

    user_settings = inputdata["user_settings"]
    agent_config = AgentConfig(user_settings_keys=user_settings["keys"])

    return "ok"