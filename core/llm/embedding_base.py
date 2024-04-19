import os
import types
from core.agent.agent_config import AgentConfig
import openai
import ollama

embedding_types = types.SimpleNamespace()
embedding_types.OPENAI = "openai"
embedding_types.LLAMA3 = "llama3"

class EmbeddingBase:
    def __init__(self, agent_config:AgentConfig):
        self.agent_config = agent_config
        openai.api_key = agent_config.OPENAI_API_KEY

    def get_embedding(self, input, embedding_type = "", embedding_model=""):

        embedding_type = self.agent_config.EMEBDDING_TYPE if embedding_type == "" else embedding_type
        default_model = self.agent_config.OPENAI_EMBEDDING_MODEL if embedding_type == embedding_types.OPENAI else self.agent_config.OLLAMA_EMBEDDING_MODEL
        embedding_model = default_model if embedding_model == "" else embedding_model

        match embedding_type:
            case embedding_types.OPENAI:
                response = openai.embeddings.create(input=input, model=embedding_model)
            case embedding_types.LLAMA3:
                result = ollama.embeddings(model=embedding_model, prompt=input)
                response = result["embedding"]

        return response
    
