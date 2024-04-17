
from elasticsearch import Elasticsearch
import json
from core.db.agent_db_base import AgentDBBase
from langchain_community.vectorstores import ElasticsearchStore
from langchain.embeddings import OpenAIEmbeddings
import logging

class AgentDBElasticVector(AgentDBBase):
    def init_db(self, index:str):
        self.db = self.db = ElasticsearchStore(
            es_connection=Elasticsearch(self.__agent_config.ELASTIC_CLOUD_ID, self.__agent_config.ELASTIC_API_KEY),
            index_name=index,
            embedding=OpenAIEmbeddings(openai_api_key = self.__agent_config.OPENAI_API_KEY, 
            model = self.__agent_config.EMBEDDING_MODEL)
        )
        self.__index = index
        
    def similarity_search(self, input:str):
        context_results =  self.__store.similarity_search(input, k = self.__agent_config.ES_NUM_DOCS)
        return context_results
    
    def multi_get(self, docs:list[object]):
        result = self.db.mget(self.__index, docs)
        return [json.loads(doc["_source"]["tool"].replace("\n",""))["function"] for doc in result["docs"]]

    def get(self, id):
        result = self.db.get(self.__index,id)
        return [json.loads(doc["_source"]["tool"].replace("\n",""))["function"] for doc in result["docs"]]

    def __index(self, doc:object, ttl:int):
        return self.db.index(index=self.self.index, document= doc)


