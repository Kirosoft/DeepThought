from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase
from urllib.parse import unquote
from core.middleware.loader import Loader
import json
import logging
import urllib3

urllib3.disable_warnings()

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)
class Context:

    def __init__(self, agent_config, user_id, tenant):
        self.agent_config = agent_config
        self.db_contexts_user = AgentDBBase(self.agent_config, self.agent_config.INDEX_CONTEXTS, user_id, tenant)
        self.db_contexts_system = AgentDBBase(self.agent_config, self.agent_config.INDEX_CONTEXT, "system", "system")

    def load_all_contexts(self):
        system_contexts = list(self.db_contexts_system.get_all())
        user_contexts = list(self.db_contexts_user.get_all())

        # TODO: tenant contexts?
        return { "system_contexts": system_contexts, "user_contexts": user_contexts}

    def save_context(self, context, level = "user"):
        # TODO: split out context data to be context seachable?
        if level == "user":
            context["level"] = "user"
            return self.db_contexts_user.index(context["name"], context)
        elif level == "system" or self.tenant=="system":
            context["level"] = "system"
            return self.db_contexts_system.index(context["name"], context)


    def get_context(self, context_name: str) -> str:
        
        # determine context, default user_id, default tenant
        result = self.db_contexts_user.get(context_name)

        if result is None:
            result = self.db_contexts_system.get(context_name)
            
            if result is None:
                logging.error(f"Request context not found {context_name}")
                return None

        return result

        
    def delete_context(self, context_name, level = "user"):
        
        if (level == "user"):
            return self.db_contexts_user.delete(context_name)
        else:
            return self.db_contexts_system.delete(context_name)



    def run_context(self, context_name:str):

        context = self.get_context(context_name)

        if self.loader is None:
            self.loader = Loader()

        context = self.loader.get_context(context_name)

        args = self.get_args(context)

        self.loader.run(context["loader_name"], args)
    






