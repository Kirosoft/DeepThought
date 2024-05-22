
import azure.functions as func
import logging
from core.security.security_utils import validate_request, create_jwt
import azure.functions as func
import json

security = func.Blueprint()

@security.function_name(name="request_auth")
@security.route(auth_level=func.AuthLevel.ANONYMOUS)
def request_auth(req: func.HttpRequest) -> func.HttpResponse:  
    logging.info('request_auth')

    response = validate_request(req, True)

    if type(response) is func.HttpResponse:
        return response
    else:
        response_headers = response["response_headers"]
        user_settings = response["user_settings"]
        user_id = response["user_id"]

    # create token
    token = json.dumps({"token":create_jwt(user_id, user_settings["secret_key"])}, 
                        ensure_ascii=False).encode('utf8')

    return func.HttpResponse(token, headers=response_headers, status_code=200)
    
