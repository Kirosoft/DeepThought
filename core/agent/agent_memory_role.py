import logging
import math

from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase
from core.middleware.context import Context
from core.llm.embedding_base import EmbeddingBase

import numpy as np
import logging

class AgentMemoryRole:
    def __init__(self, agent_config:AgentConfig, user_id, tenant, context = ""):
        self.agent_config = agent_config
        self.tenant = tenant
        self.user_id = user_id
        self.context = context
        self.memory = {}
        self.__init_store(user_id, tenant)


    def __init_store(self, user_id, tenant):
        
        self.user_roles = AgentDBBase(self.agent_config, self.agent_config.INDEX_ROLES, user_id, tenant)
        self.embedding = EmbeddingBase(self.agent_config)

        roles = self.user_roles.get_all()

        for id, role in enumerate(roles):
            embedding_vector=self.embedding.get_embedding(role["name"] + " "+role["description"] +" " + role["role"]+ " "+ role["expected_input"]).data[0].embedding
            role["embedding"] = embedding_vector
            self.memory[id] = role


    def embedding_to_lsh(self, embedding, num_planes=10, seed=123):

        # Generate a set of random planes (vectors) for the projection
        planes = np.random.normal(size=(num_planes, len(embedding)))

        # Project the embedding onto each plane and binarize the results
        projections = np.dot(planes, embedding)
        binary_projections = (projections >= 0).astype(int)

        # Convert the binary projections to a string hash
        hash_str = ''.join(str(bit) for bit in binary_projections)

        # Return the hash as a string
        return hash_str

    def cosine_similarity(self, v1, v2):
        dot_product = 0
        norm1 = 0
        norm2 = 0
        for i in range(len(v1)):
            dot_product += v1[i] * v2[i]
            norm1 += v1[i] * v1[i]
            norm2 += v2[i] * v2[i]
        
        norm1 = math.sqrt(norm1)
        norm2 = math.sqrt(norm2)
        similarity = dot_product / (norm1 * norm2)
        return similarity
    
    def get_context(self, input_data, min_threshold = 0.20):
        highest_score = -1
        highest_id = -1

        # convert the input data into a vector
        input_vector = self.embedding.get_embedding(input_data).data[0].embedding

        for id in self.memory.keys():
            score =self.cosine_similarity(input_vector, self.memory[id]["embedding"])
            print(f"id {id} score: {score}")
            self.memory[id]["similarity"] = score

            if score > highest_score:
                highest_score = score
                highest_id = id
        
        top_role = self.memory[highest_id].copy() if highest_id != -1 and highest_score > min_threshold else None

        if top_role is not None:
            del top_role["embedding"]

        return top_role


