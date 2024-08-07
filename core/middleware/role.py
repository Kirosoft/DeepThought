from core.agent.agent_config import AgentConfig
from core.agent.agent_memory_role import AgentMemoryRole
from core.db.agent_db_base import AgentDBBase
from core.middleware.context import Context
from urllib.parse import unquote
import json
import logging
import urllib3

urllib3.disable_warnings()

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

class Role:

    def __init__(self, agent_config, user_id, tenant):
        self.agent_config = agent_config
        self.user_id = user_id
        self.tenant = tenant
        self.db_roles_user = AgentDBBase(self.agent_config, self.agent_config.INDEX_ROLES, user_id, tenant)
        self.db_roles_system = AgentDBBase(self.agent_config, self.agent_config.INDEX_ROLES, "system", "system")
        self.agent_memory_roles = AgentMemoryRole(agent_config, user_id, tenant)
        self.context = Context(agent_config, user_id, tenant)

    def load_all_roles(self):
        system_roles = list(self.db_roles_system.get_all())
        user_roles = list(self.db_roles_user.get_all())

        # TODO: tenant roles?
        return { "system_roles": system_roles, "user_roles": user_roles}

    def save_role(self, role, level = "user"):
        # TODO: split out role data to be context seachable?
        if level == "user":
            role["level"] = "user"
            return self.db_roles_user.index(role["name"], role)
        elif level == "system" or self.tenant=="system":
            role["level"] = "system"
            return self.db_roles_system.index(role["name"], role)


    def get_role(self, role_name: str, input_data) -> str:
        
        # determine role, default user_id, default tenant
        # if the role name is 'auto' then semantically lookup the closest role
        if role_name=="auto":
            result = self.agent_memory_roles.get_context(input_data)
        else:
            result = self.db_roles_user.get(role_name)

        if result is None:
            result = self.db_roles_system.get(role_name)
            
            if result is None:
                logging.error(f"Request role not found {role_name}")
                return None

        # check for role_override
        if "options" in result and "role_override" in result["options"] and result["options"]["role_override"] and "role_override_context" in result["options"]:
            # load the context to inject the role - assumed text mode at the moment
            context_data_db = self.context.get_latest_context_data(result["options"]["role_override_context"])
            role_override_context = AgentDBBase(self.agent_config, context_data_db, self.user_id, self.tenant)
            override_role = role_override_context.get(result["name"]+".role")
            if override_role is not None:
                result["role"] = override_role['content']
            override_schema = role_override_context.get(result["name"]+".schema")
            if override_schema is not None:
                result["schema"] = override_schema['content']

        return result

    def get_context(self, role, agent_config:AgentConfig = None):
        # agentconfig input definition can override role based context
        if agent_config is not None and agent_config.inputs is not None and 'context' in agent_config.inputs:
            return agent_config.inputs["context"]
        elif "options" in role and "context" in role["options"]:
            return role["options"]["context"]
        else:
            return ""
        
    def get_icl_context(self, role, agent_config:AgentConfig = None):
        # agentconfig input definition can override role based context
        if agent_config is not None and agent_config.inputs is not None and 'icl_context' in agent_config.inputs:
            return agent_config.inputs["icl_context"]
        elif "options" in role and "icl_context" in role["options"]:
            return role["options"]["icl_context"]
        else:
            return ""
        
    def is_rag(self, role, agent_config:AgentConfig = None) -> bool:
        is_rag = False

        try:
            if agent_config is not None and agent_config.inputs is not None and 'context' in agent_config.inputs and agent_config.inputs["context"] != '':
                return True
            elif "options" in role and "context" in role["options"] and role["options"]["context"] != '':
                return True
        except Exception as err:
            logging.info(f"Rag option not set {err}")

        return is_rag
        
    def is_icl(self, role, agent_config:AgentConfig = None) -> bool:
        is_icl = False

        try:
            if agent_config is not None and agent_config.inputs is not None and 'icl_context' in agent_config.inputs and agent_config.inputs["icl_context"] != '':
                return True
            elif "options" in role and "icl_context" in role["options"] and role["options"]["icl_context"] != '':
                return True
        except Exception as err:
            logging.info(f"ICL option not set {err}")

        return is_icl
        
    def delete_role(self, role_name, level = "user"):
        
        if (level == "user"):
            return self.db_roles_user.delete(role_name)
        else:
            return self.db_roles_system.delete(role_name)



    