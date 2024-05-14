
from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase
from core.llm.embedding_base import EmbeddingBase

import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos import PartitionKey
import logging
import json

# Partion key: {tenant}{user_id}{index}
# 'default' tenant will hold most users data
# 'system' tenant and 'system' user will hold system level role, spec and tool definitions
# 'tenant' and 'system' user will handle coporate level role definitions
#
class AgentDBCosmos(AgentDBBase):
    def __init__(self, agent_config:AgentConfig, data_type:str, user_id:str, tenant:str, partition_key, container_name):
        self.__agent_config = agent_config
        self.__data_type = data_type
        self.embedding = EmbeddingBase(self.__agent_config)
        self.partition_key = partition_key
        self.container = None
        self.tenant = tenant
        self.user_id = user_id
        self.container_name = container_name

    def init_db(self):

        # Create a Cosmos DB client
        self.client = cosmos_client.CosmosClient(self.__agent_config.COSMOS_ENDPOINT, {"masterKey": self.__agent_config.COSMOS_KEY}) 
#                                                 _user_agent="deepthought_import_roles", user_agent_overwrite=True)
        self.client.create_database_if_not_exists(self.__agent_config.DATABASE_NAME)
        self.database = self.client.get_database_client(self.__agent_config.DATABASE_NAME)

        self.container = None
        return self.database
    
    def set_db(self, db):
        self.database = db

    def get_container(self):

        if self.container is None:
            return self.init_container()
        else:
            return self.container
    
    def init_container(self):
        # This defines the location of the partition key 
        self.database.create_container_if_not_exists(self.container_name, PartitionKey(path=self.partition_key, kind="MultiHash"))
        self.container = self.database.get_container_client(self.container_name)

        if self.__agent_config.AzureDBSetupFunctions == "true":
            # make sure the UDF is registered
            try:
                udf = self.container.scripts.get_user_defined_function("cosineSimilarity")
            except:
                self.container.scripts.create_user_defined_function(udf_definition)

            try:
                self.created_sproc = self.container.scripts.get_stored_procedure(sproc="spSimilaritySearch") 
            except:
                self.created_sproc = self.container.scripts.create_stored_procedure(body=sproc) 

            try:
                self.delete_sproc = self.container.scripts.get_stored_procedure(sproc="spDeleteSproc") 
            except:
                self.delete_sproc = self.container.scripts.create_stored_procedure(body={
                                                                                    'id': 'spDeleteSproc',
                                                                                    'serverScript': delete_index_sproc,
                                                                                }) 
                
        return self.container

    def get(self, id:str, user_id = None, tenant = None):
        try:
            # if user_id and tenant are not supplied override with the defaults
            user_id = user_id if user_id is not None else self.user_id
            tenant = tenant if tenant is not None else self.tenant
            data = self.get_container().read_item(item=id, partition_key=[tenant, user_id, self.__data_type])
        except Exception  as err:
            data = None
            logging.warning(f"{err} Could not find {id} in ${self.index} with partition_key {[tenant, user_id, self.__data_type]}")

        return data

    def multi_get(self, docs:list[object], user_id = None, tenant = None):
        user_id = user_id if user_id is not None else self.user_id
        tenant = tenant if tenant is not None else self.tenant

        query = f"SELECT * FROM C where C.id in ('{','.join(docs)}')"
        result = self.get_container().query_items(query, enable_cross_partition_query=True, partition_key=[self.tenant, self.user_id, self.__data_type])
        return result


    def get_session(self, session_token:str):
        user_id = user_id if user_id is not None else self.user_id
        tenant = tenant if tenant is not None else self.tenant

        query = f"SELECT * FROM C where C.session_token = '{session_token}'"
        result = self.get_container().query_items(query, enable_cross_partition_query=True, partition_key=[self.tenant, self.user_id, self.__data_type])
        return result

    def similarity_search_vector(self, input_vector, distance_threshold=0.5, top_k = 5):

        parameters = [
            input_vector,
            distance_threshold,
            top_k
        ]
        
        try:
            result = self.get_container().scripts.execute_stored_procedure(sproc="spSimilaritySearch",params=parameters, partition_key=[self.tenant, self.user_id, self.__data_type]) 
        except Exception as err:
            result = "[]"
        
        return json.loads(result)

    def similarity_search(self, input:str, distance_threshold=0.5, top_k = 5):
        result=self.embedding.get_embedding(input)
        vector = result.data[0].embedding
        return self.similarity_search_vector(vector, distance_threshold, top_k)

    def delete_index(self):

        query = f"SELECT * FROM c"

        parameters = [
            query
        ]
        
        try:
            result = self.get_container().scripts.execute_stored_procedure(sproc="spDeleteSproc",params=parameters, partition_key=[self.tenant, self.user_id, self.__data_type]) 
        except Exception as err:
            result = "[]"
        
        return result


    def index(self, id:str, doc:object, ttl=-1):

        doc["id"] = id
        #doc["partition_key"] = self.partition_key
        doc["ttl"] = ttl
        doc["data_type"] = self.__data_type
        doc["tenant"] = self.tenant
        doc["user_id"] = self.user_id

        self.get_container().upsert_item(body=doc)



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

delete_index_sproc = """
function deleteSproc(query) {
    var collection = getContext().getCollection();
    var collectionLink = collection.getSelfLink();
    var response = getContext().getResponse();
    var responseBody = {
        deleted: 0,
        continuation: ""
    };

    // Validate input.
    if (!query) throw new Error("The query is undefined or null.");

    tryQueryAndDelete();

    function tryQueryAndDelete(continuation) {
        var requestOptions = {
            continuation: continuation, 
            pageSize: 10
        };

        var isAccepted = collection.queryDocuments(collectionLink, query, requestOptions, function (err, documents, responseOptions) {
            if (err) throw err;

            if (documents.length > 0) {
                tryDelete(documents);
                if(responseOptions.continuation){
                    tryQueryAndDelete(responseOptions.continuation);
                }else{
                    response.setBody(responseBody);
                }

            }
        });

        if (!isAccepted) {
            response.setBody(responseBody);
        }
    }

    function tryDelete(documents) {
        if (documents.length > 0) {
            var requestOptions = {etag: documents[0]._etag};

            // Delete the document.
            var isAccepted = collection.deleteDocument(
                documents[0]._self, 
                requestOptions, 
                function (err, updatedDocument, responseOptions) {
                    if (err) throw err;

                    responseBody.deleted++;
                    documents.shift();
                    // Try updating the next document in the array.
                    tryDelete(documents);
                }
            );

            if (!isAccepted) {
                response.setBody(responseBody);
            }
        } 
    }
}
"""