import logging
from datetime import datetime, timezone, timedelta
from azure.cosmos.exceptions import CosmosResourceNotFoundError
import jwt

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

def get_user_context(user_id):
    userdb = AgentDBBase(agent_config, agent_config.INDEX_USER, "/user")
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
        userdb.index(user_id, user_settings)

    return user_settings

def process_request(body, tenant, user_id):
    agent_config.update_from_body(body)
     
    if agent_config.is_valid():
        logging.info('core_llm_agent processed an event: %s',agent_config.input)
        agent_role = AgentRole(agent_config, tenant, user_id)
        agent_memory = AgentMemory(agent_config, tenant, user_id)

        llm = LLMBase(agent_config)

        # use the configured role to find the prompt and populate with the context and session history as required
        completed_prompt = agent_role.get_completed_prompt(agent_config.role)

        #llm_result = agent_llm.run_inference(completed_prompt, agent_config.input, agent_config.role, tools, routing)
        llm_result = llm.inference(completed_prompt)

        agent_memory.save_session_history(llm_result)

        return llm_result
    else:
        return None

def save_role(role, tenant, user_id):
    agent_role.save_role(json.loads(role), tenant, user_id)

def get_role(role, tenant, user_id, tenant, user_id):
    return agent_role.get_role(role_name, tenant, user_id)

def get_roles(role, tenant, user_id):
    return agent_role.get_roles(role_name, tenant, user_id)

def create_jwt(user_id, secret_key):
    """Create a JWT with a specified expiration time and issued at timestamp."""
    payload = {
        'sub': user_id,  # Example user ID
        'exp': datetime.now(timezone.utc) + timedelta(minutes=int(agent_config.TOKEN_EXPIRY_MINUTES)),  # Token expires in 5 minutes
        'iat': datetime.now(timezone.utc)
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token

