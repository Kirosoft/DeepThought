
import azure.functions as func
import logging
from core.security.security_utils import validate_request
import json
from core.agent.agent_config import AgentConfig
from core.middleware.role import Role

roles = func.Blueprint()

@roles.function_name(name="roles_crud")
@roles.route(auth_level=func.AuthLevel.ANONYMOUS)
def roles_crud(req: func.HttpRequest) -> func.HttpResponse:  

    logging.info('roles CRUD')

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
                role = Role(agent_config, user_settings["user_id"], user_settings["user_tenant"])
                result = role.save_role(json_body)
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
                role = Role(agent_config, user_settings["user_id"], user_settings["user_tenant"])
                result = role.delete_role(item_id)
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
                role = Role(agent_config, user_settings["user_id"], user_settings["user_tenant"])
                if item_id is not None:
                    result = role.get_role(item_id)
                else:
                    result = role.load_all_roles()

                logging.info('Loaded roles')
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
