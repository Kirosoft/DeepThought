import logging

from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase

class AgentMemory:
    def __init__(self, agent_config:AgentConfig, tenant, user_id):
        self.__agent_config = agent_config

        self.__init_store()

    def __init_store(self):
        # connect to a db and intialise a connection to the vector store
        # TODO: make sure the tenant and userid are used to form a hierarchical key
        self.__context_store = AgentDBBase(self.__agent_config, self.__agent_config.INDEX_CONTEXT, "/context")
        self.__history_store = AgentDBBase(self.__agent_config, self.__agent_config.INDEX_HISTORY, "/history")

    # similarity search in the conext db
    def get_context(self, question: str):
        # context search
        context_results =  self.__context_store.similarity_search(question, 0.25, 5)
        return context_results
    
    # match * search in the session db
    def get_session_history(self, session_token:str):
        result = []

        try:
            result = self.__history_store.get_session(session_token)
        except:
            logging.warning(f'Error trying to read history from {self.__agent_config.INDEX_HISTORY}')

        return result

    def save_session_history(self, doc):

        self.__history_store.index(
            id = doc['id'],
            doc=doc
        )
