import logging

from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase

class AgentMemory:
    def __init__(self, agent_config:AgentConfig):
        self.__agent_config = agent_config

        self.__init_store()

    def __init_store(self):
        # connect to elastic and intialise a connection to the vector store
        self.__store = AgentDBBase(self.__agent_config, self.__agent_config.INDEX_HISTORY)

        # self.__store = ElasticsearchStore(
        #     es_connection=elasticsearch_client,
        #     index_name=self.__agent_config.INDEX,
        #     embedding=OpenAIEmbeddings(openai_api_key = self.__agent_config.OPENAI_API_KEY, 
        #     model = self.__agent_config.EMBEDDING_MODEL)
        # )

    def get_context(self, question: str):
        # context search
        context_results =  self.__store.similarity_search(question, k = self.__agent_config.TOP_K_DOCS)
        return context_results
    
    def get_session_history(self, session_token:str):
        try:
            result = self.__store.client.search(index=self.__agent_config.INDEX_HISTORY, query={"match": {"session_token": session_token}})
            if result['hits']['total']['value'] > 0:
                return result["hits"]['hits']
            else:
                return []
        except:
            logging.warning(f'Error trying to read history from {self.__agent_config.INDEX_HISTORY}')

            return []
