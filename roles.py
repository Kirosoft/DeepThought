
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
    agent_config = AgentConfig(body) if body != '' else AgentConfig()

    if req.method == "POST":
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
    if req.method == "DELETE":
        try:
            item_id = req.params.get('id')
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
    elif req.method == "GET":
        try:
            item_id = req.params.get('id')
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
    else:
        return func.HttpResponse("Method not allowed", status_code=405, headers=response_headers)
