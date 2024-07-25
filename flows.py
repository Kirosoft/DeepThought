import azure.functions as func
import azure.durable_functions as df
import os
import traceback
from datetime import timedelta

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

    headers = dict(req.headers)
    response_headers = response["response_headers"]
    instance_id = req.params.get("instance_id", "")
    question = req.params.get("question", "")
    flow_name = req.params.get("flow_name", "")
    payload = response["payload"]

    try:
        user_settings = response["user_settings"]
        data = {"instance_id":instance_id, "question":question, "user_settings":user_settings, "flow_name":flow_name, "headers":headers}
        graph_run_id = await client.start_new("wait_for_entity_signal", None, data)

        logging.info(f'completion events raised {graph_run_id}')

        try:
            # Wait for the orchestration to complete with a timeout
            result = await client.wait_for_completion_or_create_check_status_response(
                request=req,
                instance_id=graph_run_id,
                timeout_in_milliseconds=30000,  # 30 seconds timeout
                retry_interval_in_milliseconds=500  # Check every half second
            )
            
            if result:
                return func.HttpResponse(result.get_body())
            else:
                return func.HttpResponse("Orchestration timed out", status_code=408)
        
        except Exception as e:
            return func.HttpResponse(f"An error occurred: {str(e)}", status_code=500)

    except Exception as e:
        return func.HttpResponse("An error occurred during processing", status_code=500)

@df_flows.orchestration_trigger(context_name="context")
def wait_for_entity_signal(context: df.DurableOrchestrationContext):

    flow_params = context.get_input()
    user_settings=flow_params["user_settings"]
    agent_config = AgentConfig(user_settings_keys=user_settings["keys"])
    flow_crud = Flow(agent_config, user_settings["user_id"], user_settings["user_tenant"])
    flow_groups = flow_crud.get_flow_groups(flow_params["flow_name"])
    flow = flow_crud.get_flow(flow_params["flow_name"])

    for level, node_list in enumerate(flow_groups):
        node_group = []
        node_group.append(node_list)
        for node in node_group:
            # user input
            payload = {"input": flow_params["question"]}
            operation = node["type"].split('/')[0]
            role = node['type'].split('/')[1]
            payload["operation"] = operation
            payload["role"] = role
            # connect based inputs
            payload["inputs"] = {}

            input_nodes = flow_crud.get_linked_input_nodes(flow, node)
            # GET - these can be done in parallel (collect all input data)
            previous_node_data = [previous_node["id"] for previous_node in input_nodes.values()] if level > 0  else []

            for link in input_nodes:
                payload["inputs"][link] = yield context.call_entity(df.EntityId("flow_node", f"{flow_params['instance_id']}-{input_nodes[link]['id']}"), "get_result", {})
           
            # PROCESS these can be done in parallel
            host_name = os.environ.get('WEBSITE_HOSTNAME','localhost:7071')
            
            try:
                result = ''
                match(payload['operation']):
                    case 'role':
                        resp = yield context.call_http("POST", f"http://{host_name}/api/run_agent",payload, headers=flow_params["headers"])
                        result = resp["content"] if resp["content"]  else {}
                    case 'context': 
                        result= payload["role"]
                    # event nodes are not processed this way
                    case 'events': 
                        break
                    case 'basic':
                        match(payload['role']):
                            # input nodes - take input from outside the flow
                            case 'input':
                                result = payload["input"]
                            # output nodes - carry the results that will be sent outside the flow
                            case 'output':
                                result= payload["inputs"]
                            # context nodes - placeholder to specific a context definition
                            # can be used as input to any linked nodes

                # set the entity result value
                res = yield context.call_entity(df.EntityId("flow_node", f"{flow_params['instance_id']}-{node['id']}"), "set_result", result)
            except Exception as e:
                logging.error(f"wait_for_entity_signal: {traceback.format_exc()}")


    # collect the output values from the last row of nodes
    result = []
    groups = []
    groups.append(flow_groups[-1])
    for out in groups:
        node = yield context.call_entity(df.EntityId("flow_node", f"{flow_params['instance_id']}-{out['id']}"), "get_result", {})
        result.append(node)

    return result

# runs the flow - used to setup the DAG
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
    headers = dict(req.headers)

    input = {
        "user_settings":user_settings,
        "id":req.params.get("id",""),
        "headers": headers
    }
    # TODO: validate the user identity here??

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
    headers = input_data["headers"]

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
            yield context.call_entity(entity_id, "setup_node", node)
        
        event_nodes = flow_crud.find_nodes(flow, 'events/timer')
        timer_map = {}
        timer_tasks = []
        for event_node in event_nodes:
            interval = event_node["properties"]["interval"] if 'interval' in event_node["properties"] else 10000
            timer_event = context.create_timer(context.current_utc_datetime + timedelta(seconds=interval))
            timer_map[timer_event] = event_node
            timer_tasks.append(timer_event)
        question_event = context.wait_for_external_event("question")

        while not finished:
            winner = yield context.task_any(timer_tasks)

            if winner in timer_tasks:
                logging.error(f"Timer expired {timer_map[winner]['id']}")
                timer_index = timer_tasks.index(winner)
                expired_node = timer_map[winner]
                interval = expired_node["properties"]["interval"] if 'interval' in expired_node["properties"] else 10000
                timer_tasks[timer_index] = context.create_timer(context.current_utc_datetime + timedelta(seconds=interval))
                
                # remove the old one
                del timer_map[winner]
                timer_map[timer_tasks[timer_index]] = expired_node

                # # start a new one
                # 
                # timer_event = 
                # timer_map[timer_event] = expired_node
                # timer_tasks.append(timer_event)

                # 1. find the linked output nodes (only context nodes)
                output_nodes = flow_crud.get_linked_nodes(flow, expired_node)
                # 2. call the loader function
                for out_node in output_nodes:
                    # only context nodes can be triggered by events
                    if out_node["type"].split('/')[0] == "context":
                        base_url = os.environ.get('WEBSITE_HOSTNAME','localhost:7071')
                        context_definition_name = out_node["type"].split('/')[1]
                        url = f"http://{base_url}/api/run_context?id={context_definition_name}"
                        r = yield context.call_http("Get", url, headers=headers)
                        logging.error(f"Called {str(r)}")

            elif winner == question_event:
                question_event = context.wait_for_external_event("question")

    except Exception as e:
        logging.error(f"Error in orchestrate flow{str(e)}")
        raise
    finally:
        for node in flow_nodes:
            entity_id = df.EntityId("flow_node", f"{context.instance_id}-{node['id']}")
            context.signal_entity(entity_id, "delete")

        logging.error(f"Orchestrate flow ***Terminated***")

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
def flow_node(context:df.DurableEntityContext):
    current_value = context.get_state(lambda: {})
    match context.operation_name:
        case "setup_node":
            try:
                input_data = context.get_input()
                current_value["node_info"] = input_data
                current_value["result"] = ""
                context.set_state(current_value)
            except Exception as e:
                logging.error(f"Error in flow_node {str(e)}")

        case "set_result":
            try:
                input_data = context.get_input()
                current_value["result"] = input_data
                context.set_state(current_value)
            except Exception as e:
                logging.error(f"Error in flow_node {str(e)}")
        case "get_result":
            context.set_result(current_value["result"])
        case "delete":
            context.delete_state()


