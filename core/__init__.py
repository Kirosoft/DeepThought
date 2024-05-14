import logging
from datetime import datetime, timezone, timedelta
from azure.cosmos.exceptions import CosmosResourceNotFoundError
import jwt
import azure.functions as func

# Local 
#from core.agent.agent_llm import AgentLLM
from core.agent.agent_role import AgentRole
from core.agent.agent_config import AgentConfig
from core.agent.agent_memory import AgentMemory
from core.db.agent_db_base import AgentDBBase
from core.llm.llm_base import LLMBase

agent_config = AgentConfig()

class RateLimitError(Exception):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, message="Rate Limit Error"):
        self.message = message
        super().__init__(self.message)

class CreditBalanceError(Exception):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, message="Credit Balance Error"):
        self.message = message
        super().__init__(self.message)

response_headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',  # Disallow any origin not in allowed_origins
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, x-user-id,x-password'
}

def get_user_context(user_id):
    userdb = AgentDBBase(agent_config, agent_config.INDEX_USER, user_id, "system")
    user_settings = userdb.get(user_id)

    # Attempt to find existing rate limit entry
    current_time = datetime.now(timezone.utc)
    try:
        request_count = user_settings['count']
        last_request_time = datetime.fromisoformat(user_settings['last_request_time'])
        
        # Check rate limit
        if request_count >= user_settings["rate_limit"] and (current_time - last_request_time).total_seconds() < user_settings["rate_window_seconds"]:
            raise RateLimitError() 
        
        # Update request count or reset if time window has passed
        if (current_time - last_request_time).total_seconds() >= user_settings["rate_window_seconds"]:
            user_settings['count'] = 1
            user_settings['last_request_time'] = current_time.isoformat()
        else:
            user_settings['count'] += 1
       
        if user_settings['credit_balance'] >= 1:
            user_settings['credit_balance'] -= 1
        else:
            raise CreditBalanceError()

        userdb.index(user_id, user_settings)

    except (CosmosResourceNotFoundError, KeyError) as e:
        # Create new entry if not found
        user_settings["count"] = 1
        user_settings["last_request_time"] = current_time.isoformat()
        user_settings["rate_limit"] = 10
        user_settings["rate_window_seconds"] = 60

        userdb.index(user_id, user_settings)

    return user_settings

def process_request(body, user_id, tenant):
    agent_config.update_from_body(body)
     
    if agent_config.is_valid():
        logging.info('core_llm_agent processed an event: %s',agent_config.input)
        agent_role = AgentRole(agent_config, user_id, tenant)
        agent_memory = AgentMemory(agent_config, user_id, tenant)

        llm = LLMBase(agent_config)

        # use the configured role to find the prompt and populate with the context and session history as required
        completed_prompt = agent_role.get_completed_prompt(agent_config.role)

        #llm_result = agent_llm.run_inference(completed_prompt, agent_config.input, agent_config.role, tools, routing)
        llm_result = llm.inference(completed_prompt)

        agent_memory.save_session_history(llm_result)

        return llm_result
    else:
        return None

def create_jwt(user_id, secret_key):
    """Create a JWT with a specified expiration time and issued at timestamp."""
    payload = {
        'sub': user_id,  # Example user ID
        'exp': datetime.now(timezone.utc) + timedelta(minutes=int(agent_config.TOKEN_EXPIRY_MINUTES)),  # Token expires in 5 minutes
        'iat': datetime.now(timezone.utc)
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token

def validate_request(req: func.HttpRequest, isAuth = False): 
    # Handle preflight requests
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=response_headers)

    if not isAuth:
        auth_header = req.headers.get('Authorization')
        if not auth_header:
            return func.HttpResponse("Authorization header is missing", status_code=401)

    user_id = req.headers.get('x-user-id')  # Assume user ID is passed in header for simplicity
    if not user_id:
        return func.HttpResponse("User ID is required", status_code=400)
    
    try:
        user_settings = get_user_context(user_id)
    except RateLimitError as e:
        return func.HttpResponse("Rate limit exceeded", status_code=429)
    except CreditBalanceError as e:
        return func.HttpResponse("Credit limit balance is zero", status_code=429)

    # Get the request origin
    # request_origin = req.headers.get('Origin')
    # if request_origin in user_settings["origins"]:
    #     response_headers['Access-Control-Allow-Origin'] = request_origin,  # Echo the origin back

    if isAuth:
        password = req.headers.get('x-password') 
        if not password:
            return func.HttpResponse("password header is required", status_code=400)
        elif password != user_settings["password"]:
            return func.HttpResponse("account credentials do not match", status_code=400)
        # success
        return {"payload":None, "response_headers":response_headers, "user_settings":user_settings, "user_id":user_id}
    
    auth_header = req.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return func.HttpResponse("Unauthorized: No token provided", status_code=401, headers=response_headers)

    token = auth_header.split(' ')[1]
    try:
        # Decode and validate JWT
        # Adjust 'algorithms' based on your JWT's signing algorithm
    
        payload = jwt.decode(token, user_settings["secret_key"], algorithms=["HS256"])
        # TODO: cross validate the headeruserid with the decrypted userid
        # happy path
        return {"payload":payload, "response_headers":response_headers, "user_settings":user_settings, "user_id":user_id}

    except jwt.ExpiredSignatureError:
        return func.HttpResponse("Token expired", status_code=401, headers=response_headers)
    except jwt.InvalidTokenError:
        return func.HttpResponse("Invalid token", status_code=401, headers=response_headers)
    except e:
        return func.HttpResponse(f"Unknown auth error {e}",status_code=401, headers=response_headers)
