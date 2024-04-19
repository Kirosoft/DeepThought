import logging

from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase

class AgentMemory:
    def __init__(self, agent_config:AgentConfig):
        self.__agent_config = agent_config

        self.__init_store()

    def __init_store(self):
        # connect to a db and intialise a connection to the vector store
        self.__context_store = AgentDBBase(self.__agent_config, self.__agent_config.INDEX_CONTEXT)
        self.__history_store = AgentDBBase(self.__agent_config, self.__agent_config.INDEX_HISTORY)

    # similarity search in the conext db
    def get_context(self, question: str):
        # context search
        context_results =  self.__context_store.similarity_search(question, 0.7)
        return context_results
    
    # match * search in the session db
    def get_session_history(self, session_token:str):
        try:
            result = self.__history_store.client.search(index=self.__agent_config.INDEX_HISTORY, query={"match": {"session_token": session_token}})
            if result['hits']['total']['value'] > 0:
                return result["hits"]['hits']
            else:
                return []
        except:
            logging.warning(f'Error trying to read history from {self.__agent_config.INDEX_HISTORY}')

            return []
