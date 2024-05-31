import logging

from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase
from core.middleware.context import Context
class AgentMemory:
    def __init__(self, agent_config:AgentConfig, user_id, tenant, context = ""):
        self.agent_config = agent_config
        self.tenant = tenant
        self.user_id = user_id
        self.context = context

        self.__init_store(user_id, tenant)

    def __init_store(self, user_id, tenant):
        # connect to a db and intialise a connection to the vector store
        context_crud = Context(self.agent_config, self.user_settings["user_id"], self.user_settings["user_tenant"])
        context_name = self.context if self.context != "" else "default"

        # find the latest version of this context
        # default to version 1 if none found
        version = 1

        try:
            context_definition = context_crud.get_context(context_name)
            version = context_definition["current_version"] if "current_version" in context_definition else 1
        except Exception as err:
            raise Exception("Could not find context config defintion {self.context} {err}")
        

        self.__vector_store = AgentDBBase(self.agent_config, 
                                f"{self.agent_config.INDEX_VECTOR}{'' if context_name=='' else '_'}{context_name}_v{version}", user_id, tenant)
        self.__history_store = AgentDBBase(self.agent_config, self.agent_config.INDEX_HISTORY, user_id, tenant)

    # similarity search in the conext db
    def get_context(self, question: str):
        # context search
        context_results =  self.__vector_store.similarity_search(question, 0.25, 5)
        return context_results
    
    # match * search in the session db
    def get_session_history(self, session_token:str):
        result = []

        try:
            result = self.__history_store.get_session(session_token)
        except:
            logging.warning(f'Error trying to read history from {self.agent_config.INDEX_HISTORY}')

        return result

    def save_session_history(self, doc):

        self.__history_store.index(
            id = doc['id'],
            doc=doc
        )
