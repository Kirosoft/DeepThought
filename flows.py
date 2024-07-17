import azure.functions as func
import azure.durable_functions as df

import logging
from core.security.security_utils import validate_request
import json
from core.agent.agent_config import AgentConfig
from core.middleware.flow import Flow
from core.security.security_utils import get_user_context

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


@df_flows.route(route="completion")
@df_flows.durable_client_input(client_name="client")
async def completion(req: func.HttpRequest, client: df.DurableOrchestrationClient) -> func.HttpResponse:  
    logging.info('completion event')

    response = validate_request(req)
    if isinstance(response, func.HttpResponse):
        return response

    response_headers = response["response_headers"]
    instance_id = req.params.get("instance_id", "")
    question = req.params.get("question", "")
    flow_name = req.params.get("flow_name", "")
    payload = response["payload"]

    try:
        user_settings = response["user_settings"]
        agent_config = AgentConfig(user_settings_keys=user_settings["keys"])
        flow_crud = Flow(agent_config, user_settings["user_id"], user_settings["user_tenant"])
        flow = flow_crud.get_flow(flow_name)

        for node_list in flow_crud.topological_sort(flow):
            node_group = []
            node_group.append(node_list)
            for node in node_group:
                entity_id = df.EntityId("flow_node", f"{instance_id}-{node['id']}")
                input_data = {"question": question}
                await client.signal_entity(entity_id, "process", input_data)

        logging.info('completion events raised')

        return client.create_check_status_response(req, instance_id)

    except Exception as e:
        logging.error(f"An error occurred during completion: {str(e)}")
        return func.HttpResponse("An error occurred during processing", status_code=500)


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

    instance_id = await client.start_new("orchestrate_flow",None, input)
    logging.info(f"Started orchestration with ID = '{instance_id}'.")

    return client.create_check_status_response(req, instance_id)



@df_flows.orchestration_trigger(context_name="context")
def orchestrate_flow(context: df.DurableOrchestrationContext):
    input_data = context.get_input()  # Retrieve input data
    finished = False
    result = "ok"

    # load the flow
    flow_name = input_data["id"]
    user_settings = input_data["user_settings"]

    agent_config = AgentConfig(user_settings_keys=user_settings["keys"])
    flow_crud = Flow(agent_config, user_settings["user_id"], user_settings["user_tenant"])
    flow = flow_crud.get_flow(flow_name)

    setup = {
        "flow":flow,
        "flow_name":flow_name,
        "user_settings":user_settings,
    }

    try:
        # give each entity the context data it needs
        flow_nodes = flow["nodes"]
        for node in flow_nodes:
            setup["node_id"] = node["id"]
            setup["current_node"] = node
            entity_id = df.EntityId("flow_node", f"{context.instance_id}-{node['id']}")
            input_nodes = flow_crud.get_linked_input_nodes(flow, node) 
            ids = [str(df.EntityId("flow_node", f"{context.instance_id}-{a}")) for a in input_nodes.keys()]
            input_ids = ",".join(ids)
            logging.info(f"input_nodes: {input_ids}")
            yield context.call_entity(entity_id, "setup_inputs", ids)
            yield context.call_entity(entity_id, "setup_node", node)

        while not finished:

            # find all the input nodes
            # setup an event listener for each
            question = yield context.wait_for_external_event("question")
    
            if question:
                pass

    except Exception as e:
        logging.error(f"Error in orchestrate flow{str(e)}")
        raise

    return "ok"


            
# Entity function called counter
    # setup = {
    #     "flow":flow,
    #     "flow_crud":flow_crud,
    #     "flow_name":flow_name,
    #     "user_settings":user_settings,
    #     "agent_config":agent_config
    # }
@df_flows.entity_trigger(context_name="context")
def flow_node(context):
    current_value = context.get_state(lambda: {})
    match context.operation_name:
        case "process":
            question = context.get_input()
        case "setup_node":
            try:
                input_data = context.get_input()
                current_value["node_info"] = input_data
                context.set_state(current_value)
            except Exception as e:
                logging.error(f"Error in flow_node {str(e)}")
        case "setup_inputs":
            try:
                input_data = context.get_input()
                current_value["input_ids"] = input_data
                context.set_state(current_value)
            except Exception as e:
                logging.error(f"Error in flow_node {str(e)}")
        case "get_value":
            context.set_result(current_value)
        case "get":
            context.set_result(current_value)

