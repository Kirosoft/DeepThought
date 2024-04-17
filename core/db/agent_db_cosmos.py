
from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase

import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos import PartitionKey
import numpy as np
import base64
import logging

# Define the cosine similarity UDF
udf_definition = {
    "id": "cosineSimilarity",
    "serverScript": """
        function cosineSimilarity(v1, v2) {
            var dotProduct = 0;
            var norm1 = 0;
            var norm2 = 0;
            for (var i = 0; i < v1.length; i++) {
                dotProduct += v1[i] * v2[i];
                norm1 += v1[i] * v1[i];
                norm2 += v2[i] * v2[i];
            }
            norm1 = Math.sqrt(norm1);
            norm2 = Math.sqrt(norm2);
            var similarity = dotProduct / (norm1 * norm2);
            return similarity;
        }
    """
}

class AgentDBCosmos(AgentDBBase):
    def __init__(self, agent_config:AgentConfig, index:str):
        self.__agent_config = agent_config
        self.__index = index

    def init_db(self):
        # Create a Cosmos DB client
        self.client = cosmos_client.CosmosClient(self.__agent_config.COSMOS_ENDPOINT, {"masterKey": self.__agent_config.COSMOS_KEY})
        self.client.create_database_if_not_exists(self.__agent_config.DATABASE_NAME)
        self.database = self.client.get_database_client(self.__agent_config.DATABASE_NAME)
        self.partition_key = "/partition_key"
        self.database.create_container_if_not_exists(self.__index, PartitionKey(path=self.partition_key))
        self.container = self.database.get_container_client(self.__index)

        # make sure the UDF is registered
        try:
            udf = self.container.scripts.get_user_defined_function("cosineSimilarity")
        except:
            self.container.scripts.create_user_defined_function(udf_definition)

    def get(self, id:str):
        try:
            data = self.container.read_item(item=id, partition_key=self.partition_key)
        except:
            data = None
            logging.warning(f"Could not find {id} in ${self.index} with partition_key {self.partition_key}")

        return data

    def multi_get(self, docs:list[object]):
        self.container.query_items(f"""SELECT * FROM {self.__index} as C where C.id in ({','.join(docs)})""", enable_cross_partition_query=True)

    def similarity_search(self, input_vector):
        # Define the SQL query
        query = f"SELECT top @top c.embedding, udf.cosineSimilarity(c.embedding, @query_embedding) as similarity, c.path as path FROM {self.__index} c where udf.cosineSimilarity(c.embedding, @query_embedding) >= @dist_val ORDER BY c.similarity DESC"

        # Define the query parameters
        parameters = [
            {"name": "@query_embedding", "value": input_vector},
            {"name": "@dist_val", "value": 0.25},
            {"name": "@top", "value": 5}
        ]
        # Execute the query and retrieve the results
        results = self.container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        )

        return results
    
    def index(self, id:str, doc:object, ttl=-1):

        doc["id"] = id
        doc["partition_key"] = self.partition_key
        doc["ttl"] = ttl

        self.container.upsert_item(body=doc)



