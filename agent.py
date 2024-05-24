
import azure.functions as func
import logging
from core.security.security_utils import validate_request
from core.agent.agent_role import AgentRole

import json

agent = func.Blueprint()

@agent.function_name(name="run_agent")
@agent.route(auth_level=func.AuthLevel.ANONYMOUS)
def run_agent(req: func.HttpRequest) -> func.HttpResponse:  

    logging.info('tun_agent trigger from http')

    response = validate_request(req)
    if type(response) is func.HttpResponse:
        return response
    else:
        response_headers = response["response_headers"]
        user_settings = response["user_settings"]
        payload = response["payload"]
    
    if req.method == "POST":
        try:
            agent = AgentRole(user_settings["user_id"], user_settings["user_tenant"], user_settings["keys"])
            result = agent.run_agent(req.get_body().decode('utf-8'))

            if (result != None):
                logging.info('Answer: %s',result["answer"])
                response_str = json.dumps(result, ensure_ascii=False).encode('utf8')
                return func.HttpResponse(response_str, headers=response_headers, status_code=200)
            else:
                answer_str = {"answer":"No question found, please supply a question", "answer_type":"error"}
                logging.info('Answer: %s',answer_str)
                response_str = json.dumps(answer_str, ensure_ascii=False).encode('utf8')

                return func.HttpResponse(
                    response_str,
                    status_code=200,
                    headers=response_headers
                )
        except ValueError:
            return func.HttpResponse(
                "Invalid JSON",
                status_code=400,
                headers=response_headers
            )
    else:
        return func.HttpResponse("Method not allowed", status_code=405, headers=response_headers)

