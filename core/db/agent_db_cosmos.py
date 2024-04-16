
from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase

import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos import PartitionKey
import numpy as np
import base64


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

    def init_db(self, index:str):

        self.index = index

        # Create a Cosmos DB client
        self.client = cosmos_client.CosmosClient(self.__agent_config.COSMOS_ENDPOINT, {"masterKey": self.__agent_config.COSMOS_KEY})

        self.database = self.client.get_database_client(self.__agent_config.DATABASE_NAME)
        self.partition_key = "/partition_key"
        self.database.create_container_if_not_exists(index, PartitionKey(path=self.partition_key))
        self.container = self.database.get_container_client(index)

        # make sure the UDF is registered
        try:
            udf = self.container.scripts.get_user_defined_function("cosineSimilarity")
        except:
            self.container.scripts.create_user_defined_function(udf_definition)


    def multi_get(self, docs:list[object]):
        self.container.query_items(f"""SELECT * FROM {self.index} as C where C.id in ({','.join(docs)})""", enable_cross_partition_query=True)

    def similarity_search(self, input_vector):
        # Define the SQL query
        query = f"SELECT top @top c.vector, udf.cosineSimilarity(c.vector, @query_vector) as similarity FROM ${self.__agent_config.DATABASE_NAME} c where udf.cosineSimilarity(c.vector, @query_vector) >= @dist_val"

        # Define the query parameters
        parameters = [
            {"name": "@query_vector", "value": input_vector},
            {"name": "@dist_val", "value": 0.5},
            {"name": "@top", "value": 5}
        ]
        # Execute the query and retrieve the results
        results = self.container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        )

        return results
    
    def index(self, id:str, doc:object, ttl=0):

        doc["partition_key"] = self.partition_key
        doc["ttl"] = ttl

        self.container.upsert_item(body=doc)



