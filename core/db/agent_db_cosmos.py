
from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase
from core.llm.embedding_base import EmbeddingBase

import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos import PartitionKey
import numpy as np
import base64
import logging
import json

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
            var similarity = Math.round((dotProduct / (norm1 * norm2))*100);
            return similarity;
        }
    """
}

similarity_search = """
function similarity_search(input_vector, max_dist, top_k) {
    var collection = getContext().getCollection();
    if (typeof input_vector === "string") input_vector = JSON.parse(input_vector);
    if (typeof max_dist === "string") max_dist = JSON.parse(max_dist);
    if (typeof top_k === "string") top_k = JSON.parse(top_k);
 
    console.log(`input_vector: ${input_vector}`);
    console.log(`max_dist: ${max_dist}`);
    console.log(`top_k: ${top_k}`);
    var params = [{
            'name':'@input', 'value':input_vector,
            },
            {
            'name':'@max_dist', 'value':max_dist
            }];
    var query = "SELECT r.path as path, udf.cosineSimilarity(r.embedding, @input) as udf_similarity, r.content as content FROM root r WHERE udf.cosineSimilarity(r.embedding, @input) >= @max_dist";
    var filterQuery={
        'query':query,
        'parameters':params
    }
    
    function sortFloat(a,b) { 
        return b.udf_similarity - a.udf_similarity; 
    }
    
    var isAccepted = collection.queryDocuments(
        collection.getSelfLink(),
        filterQuery,
    function (err, feed, options) {
        if (err) throw err;

        // Check the feed and if empty, set the body to 'no docs found', 
        // else take 1st element from feed
        if (!feed || !feed.length) {
            var response = getContext().getResponse();
            response.setBody(`no docs found: ${query} ${input_vector} ${max_dist} ${top_k}`);
        }
        else {
            var response = getContext().getResponse();
            feed.sort(sortFloat)
            var body = feed.slice(0,top_k); 
            response.setBody(JSON.stringify(body));
        }
    });

    if (!isAccepted) throw new Error('The query was not accepted by the server.');
}
"""

sproc = {
    'id': 'spSimilaritySearch',
    'serverScript': similarity_search,
}

class AgentDBCosmos(AgentDBBase):
    def __init__(self, agent_config:AgentConfig, index:str):
        self.__agent_config = agent_config
        self.__index = index

    def init_db(self):
        self.embedding = EmbeddingBase(self.__agent_config)

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

        try:
            self.created_sproc = self.container.scripts.get_stored_procedure(sproc="spSimilaritySearch") 
        except:
            self.created_sproc = self.container.scripts.create_stored_procedure(body=sproc) 

    def get(self, id:str):
        try:
            data = self.container.read_item(item=id, partition_key=self.partition_key)
        except:
            data = None
            logging.warning(f"Could not find {id} in ${self.index} with partition_key {self.partition_key}")

        return data

    def multi_get(self, docs:list[object]):
        query = f"SELECT * FROM {self.__index} C where C.id in ('{','.join(docs)}')"
        result = self.container.query_items(query, enable_cross_partition_query=True, partition_key=self.partition_key)
        return result


    def get_session(self, session_token:str):
        query = f"SELECT * FROM {self.__index} C where C.session_token = '{session_token}'"
        result = self.container.query_items(query, enable_cross_partition_query=True, partition_key=self.partition_key)
        return result

    def similarity_search_vector(self, input_vector, distance_threshold=0.5, top_k = 5):

        parameters = [
            input_vector,
            distance_threshold,
            top_k
        ]
        
        try:
            result = self.container.scripts.execute_stored_procedure(sproc="spSimilaritySearch",params=parameters, partition_key=self.partition_key) 
        except Exception as err:
            result = "[]"
        
        return json.loads(result)

    def similarity_search(self, input:str, distance_threshold=0.5, top_k = 5):
        result=self.embedding.get_embedding(input)
        vector = result.data[0].embedding
        return self.similarity_search_vector(vector, distance_threshold, top_k)

    def index(self, id:str, doc:object, ttl=-1):

        doc["id"] = id
        doc["partition_key"] = self.partition_key
        doc["ttl"] = ttl

        self.container.upsert_item(body=doc)



