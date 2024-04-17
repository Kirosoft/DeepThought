from core.agent.agent_config import AgentConfig
import types

# for now define supported DB types here
db_types = types.SimpleNamespace()
db_types.COSMOS = "cosmos"
db_types.ELASTIC = "elastic"
db_types.ELASTIC_VECTOR = "elastic_vector"

class AgentDBBase:
    def __init__(self, agent_config:AgentConfig, index:str):
        self.db_type = agent_config.DB_TYPE
        self.__index = index
        self.__agent_config = agent_config
        self.db_handler = self.__get_db_handler__(self.db_type)
        self.db_handler.init_db()

    # inner factory to construct the database object
    def __get_db_handler__(self, dbtype:str):

        match dbtype:
            case db_types.COSMOS:
                return AgentDBCosmos(self.__agent_config, self.__index)
            case db_types.ELASTIC:
                return AgentDBElastic()
            case db_types.ELASTIC_VECTOR:
                return AgentDBElasticVector()
            case _:
                raise Exception(f"Unknown database type: ${dbtype} requested")

    def get(self, id):
        return self.db_handler.get(id)

    def multi_get(self, id):
        self.db_handler.multi_get(id)

    def similarity_search(self, input, distance_threshold=0.5):
        return self.db_handler.similarity_search(input, distance_threshold)

    def index(self, id:str, doc:object, ttl:int = -1):
        self.db_handler.index(id, doc, ttl)


from core.db.agent_db_elastic import AgentDBElastic
from core.db.agent_db_cosmos import AgentDBCosmos
from core.db.agent_db_elastic_vector import AgentDBElasticVector


