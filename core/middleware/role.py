from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase
from urllib.parse import unquote
import json
import logging

class Role:

    def __init__(self, agent_config, user_id, tenant):
        self.agent_config = agent_config
        self.db_roles_user = AgentDBBase(self.agent_config, self.agent_config.INDEX_ROLES, user_id, tenant)
        self.db_roles_system = AgentDBBase(self.agent_config, self.agent_config.INDEX_ROLES, "system", "system")

    def load_all_roles(self):
        results = list(self.db_roles_system.get_all())
        system_roles = [json.loads(unquote(result["prompt"])) for result in results]
        results = list(self.db_roles_user.get_all())
        user_roles = [json.loads(unquote(result["prompt"])) for result in results]

        # TODO: tenant roles?
        return { "system_roles": system_roles, "user_roles": user_roles}

    def save_role(self, role):
        # TODO: split out role data to be context seachable?
        self.db_roles.index(role["name"], role)

    def get_role(self, role_name: str) -> str:
        
        if not hasattr(self, 'role'):
            # determine role, default user_id, default tenant
            result = self.db_roles_user.get(role_name)

            if result is None:
                result = self.db_roles_system.get(role_name)
                
                if result is None:
                    logging.error(f"Request role not found {role_name}")
                    return None

        return json.loads(unquote(result["prompt"]))
    
    def is_rag(self, role) -> bool:
        is_rag = False

        try:
            is_rag = role["options"]["rag_mode"]
        except Exception as err:
            logging.info(f"Rag option not set {err}")

        return is_rag
        
    



    






