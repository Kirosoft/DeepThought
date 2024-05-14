from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase



class Roles:

    def __init__(self, user_id, tenant):
        self.db_roles_user = AgentDBBase(self.__agent_config, self.__agent_config.INDEX_ROLES, user_id, tenant)
        self.db_roles_system = AgentDBBase(self.__agent_config, self.__agent_config.INDEX_ROLES, "system", "system")
        pass


    def load_roles(self, user_id, tenant):
        pass

