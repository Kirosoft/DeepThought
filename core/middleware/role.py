from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase
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
        self.db_roles_user = AgentDBBase(self.agent_config, self.agent_config.INDEX_ROLES, user_id, tenant)
        self.db_roles_system = AgentDBBase(self.agent_config, self.agent_config.INDEX_ROLES, "system", "system")

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


    def get_role(self, role_name: str) -> str:
        
        # determine role, default user_id, default tenant
        result = self.db_roles_user.get(role_name)

        if result is None:
            result = self.db_roles_system.get(role_name)
            
            if result is None:
                logging.error(f"Request role not found {role_name}")
                return None

        return result
    
    def get_context(self, role):
        if "options" in role and "context" in role["options"]:
            return role["options"]["context"]
        else:
            return ""

    def is_rag(self, role) -> bool:
        is_rag = False

        try:
            is_rag = role["options"]["context"] != ""
        except Exception as err:
            logging.info(f"Rag option not set {err}")

        return is_rag
        
    def delete_role(self, role_name, level = "user"):
        
        if (level == "user"):
            return self.db_roles_user.delete(role_name)
        else:
            return self.db_roles_system.delete(role_name)



    