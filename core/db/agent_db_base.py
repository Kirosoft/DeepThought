from core.agent.agent_config import AgentConfig
import types

# for now define supported DB types here
db_types = types.SimpleNamespace()
db_types.COSMOS = "cosmos"
db_types.ELASTIC = "elastic"
db_types.ELASTIC_VECTOR = "elastic_vector"

class AgentDBBase:

    __database = None

    # index is the type of data ee.g. role, spec, tool etc
    def __init__(self, agent_config:AgentConfig, data_type:str, user_id:str, tenant:str = "default", partition_key = ["/tenant", "/user_id", "/data_type"], container_name:str ="data"):
        self.db_type = agent_config.DB_TYPE
        self.__data_type = data_type
        self.__agent_config = agent_config
        self.user_id = user_id
        self.tenant = tenant
        self.partition_key = partition_key
        self.container_name = container_name
        self.db_handler = self.__get_db_handler__(self.db_type)

        if AgentDBBase.__database is None:
            AgentDBBase.__database = self.db_handler.init_db()
        else:
            self.db_handler.set_db(AgentDBBase.__database)


    # inner factory to construct the database object
    def __get_db_handler__(self, dbtype:str):

        match dbtype:   
            case db_types.COSMOS:
                return AgentDBCosmos(self.__agent_config, self.__data_type, self.user_id, self.tenant, self.partition_key, self.container_name)
            case db_types.ELASTIC:
                return AgentDBElastic()
            case db_types.ELASTIC_VECTOR:
                return AgentDBElasticVector()
            case _:
                raise Exception(f"Unknown database type: ${dbtype} requested")

    def get(self, id, user_id= None, tenant = None):
        return self.db_handler.get(id, user_id, tenant)

    def multi_get(self, docs):
        return self.db_handler.multi_get(docs)

    def get_session(self, session_token:str):
        return self.db_handler.get_session(session_token)

    def similarity_search(self, input, distance_threshold=0.5, top_k = 5):
        return self.db_handler.similarity_search(input, distance_threshold, top_k)

    def index(self, id:str, doc:object, ttl:int = -1):
        self.db_handler.index(id, doc, ttl)

    def delete_index(self):
        self.db_handler.delete_index()

from core.db.agent_db_elastic import AgentDBElastic
from core.db.agent_db_cosmos import AgentDBCosmos
from core.db.agent_db_elastic_vector import AgentDBElasticVector


