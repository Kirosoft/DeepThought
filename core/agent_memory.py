from langchain_community.vectorstores import ElasticsearchStore
from utils.elasticsearch_client import elasticsearch_client
from langchain.embeddings import OpenAIEmbeddings

from core.agent_config import AgentConfig

class AgentMemory:
    def __init__(self, agent_config:AgentConfig):
        self.__include_context_search = agent_config.include_context_search
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
        # use the input question to do a lookup similarity search in elastic
        # TODO: is this needed?
        self.__store.client.indices.refresh(index=self.__agent_config.INDEX)

    def use_context_search(self) -> bool:
        return self.__agent_config.include_context_search

    def use_session_history(self) -> bool:
        return self.__agent_config.session_state

    def get_context(self, question: str):
        # context search
        if self.use_context_search():
            return self.__store.similarity_search(question, k = self.__agent_config.ES_NUM_DOCS)
        else:
            return []
    
    def get_session_history(self, session_token:str):
        if self.use_session_history():
            result = self.__store.client.search(index=self.__agent_config.ES_INDEX_HISTORY, query={"match": {"session_token": session_token}})
            if result['hits']['total']['value'] > 0:
                return result["hits"]['hits']
            else:
                return []
        else:
            return []