
from elasticsearch import Elasticsearch
import json
from core.db.agent_db_base import AgentDBBase
 
class AgentDBElastic(AgentDBBase):
    def init_db(self, index:str):
        self.db = Elasticsearch(cloud_id=self.__agent_config.ELASTIC_CLOUD_ID, api_key=self.__agent_config.ELASTIC_API_KEY)
        self.__index = index
        
    def similarity_search(self, input:str):
        context_results =  self.__store.similarity_search(input, k = self.__agent_config.ES_NUM_DOCS)
        return context_results
    
    def similarity_search(self, input_vector:list[float]):
        context_results =  self.__store.similarity_search(input_vector, k = self.__agent_config.ES_NUM_DOCS)
        return context_results

    def multi_get(self, docs:list[object]):
        result = self.db.mget(self.__index, docs)
        return [json.loads(doc["_source"]["tool"].replace("\n",""))["function"] for doc in result["docs"]]

    def get(self, id):
        result = self.db.get(self.__index,id)
        return [json.loads(doc["_source"]["tool"].replace("\n",""))["function"] for doc in result["docs"]]

    def __index(self, doc:object, ttl:int):
        return self.db.index(index=self.self.index, document= doc)


