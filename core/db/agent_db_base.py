from core.agent.agent_config import AgentConfig
import types

# for now define supported DB types here
db_types = types.SimpleNamespace()
db_types.COSMOS = "cosmos"
db_types.ELASTIC = "elastic"
db_types.ELASTIC_VECTOR = "elastic_vector"

class AgentDBBase:

    __database = None

    def __init__(self, agent_config:AgentConfig, index:str, partition_key:str='partition_key'):
        self.db_type = agent_config.DB_TYPE
        self.__index = index
        self.__agent_config = agent_config
        self.partition_key = partition_key
        self.db_handler = self.__get_db_handler__(self.db_type)

        if AgentDBBase.__database is None:
            AgentDBBase.__database = self.db_handler.init_db()
        else:
            self.db_handler.set_db(AgentDBBase.__database)


    # inner factory to construct the database object
    def __get_db_handler__(self, dbtype:str):

        match dbtype:   
            case db_types.COSMOS:
                return AgentDBCosmos(self.__agent_config, self.__index, self.partition_key)
            case db_types.ELASTIC:
                return AgentDBElastic()
            case db_types.ELASTIC_VECTOR:
                return AgentDBElasticVector()
            case _:
                raise Exception(f"Unknown database type: ${dbtype} requested")

    def get(self, id):
        return self.db_handler.get(id)

    def multi_get(self, docs):
        return self.db_handler.multi_get(docs)

    def get_session(self, session_token:str):
        return self.db_handler.get_session(session_token)

    def similarity_search(self, input, distance_threshold=0.5, top_k = 5):
        return self.db_handler.similarity_search(input, distance_threshold, top_k)

    def index(self, id:str, doc:object, ttl:int = -1):
        self.db_handler.index(id, doc, ttl)


from core.db.agent_db_elastic import AgentDBElastic
from core.db.agent_db_cosmos import AgentDBCosmos
from core.db.agent_db_elastic_vector import AgentDBElasticVector


