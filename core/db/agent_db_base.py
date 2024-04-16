from agent_db_elastic import AgentDBElastic
from agent_db_cosmos import AgentDBCosmos
from core.agent_config import AgentConfig
import types

# for now define supported DB types here
db_types = types.SimpleNamespace()
db_types.COSMOS = "cosmos"
db_types.ELASTIC = "elastic"

class AgentDBBase:
    def __init__(self, agent_config:AgentConfig, index:str):
        self.db_type = agent_config.DB_TYPE
        self.__agent_config = agent_config
        self.db_handler = self.__get_db_handler__(self.db_type)
        self.init_db(self, index)

    # inner factory to construct the database object
    def __get_db_handler__(self, dbtype:str):

        match dbtype:
            case db_types.COSMOS:
                return AgentDBCosmos()
            case db_types.ELASTIC:
                return AgentDBElastic()
            case _:
                raise Exception("Unknown database type: ${dbtype} requested")

    def multi_get(self):
        pass

    def similarity_search(self, input_vector):
        pass

    def index(self, doc:object, ttl:int):
        pass

