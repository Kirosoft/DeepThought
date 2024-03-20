from langchain_community.vectorstores import ElasticsearchStore
from utils.elasticsearch_client import elasticsearch_client
from langchain.embeddings import OpenAIEmbeddings
import logging

from core.agent_config import AgentConfig

class AgentMemory:
    def __init__(self, agent_config:AgentConfig):
        self.__agent_config = agent_config

        self.__init_store()

    def __init_store(self):
        # connect to elastic and intialise a connection to the vector store
        self.__store = ElasticsearchStore(
            es_connection=elasticsearch_client,
            index_name=self.__agent_config.INDEX,
            embedding=OpenAIEmbeddings(openai_api_key = self.__agent_config.OPENAI_API_KEY, 
            model = self.__agent_config.EMBEDDING_MODEL)
        )

    def get_context(self, question: str):
        # context search
        context_results =  self.__store.similarity_search(question, k = self.__agent_config.ES_NUM_DOCS)
        return context_results
    
    def get_session_history(self, session_token:str):
        try:
            result = self.__store.client.search(index=self.__agent_config.ES_INDEX_HISTORY, query={"match": {"session_token": session_token}})
            if result['hits']['total']['value'] > 0:
                return result["hits"]['hits']
            else:
                return []
        except:
            logging.warning(f'Error trying to read history from {self.__agent_config.ES_INDEX_HISTORY}')

            return []
