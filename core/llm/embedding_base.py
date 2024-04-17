import os
import types
from core.agent.agent_config import AgentConfig
import openai

embedding_types = types.SimpleNamespace()
embedding_types.OPENAI = "openai"
embedding_types.LLAMA3 = "llama3"

class EmbeddingBase:
    def __init__(self, agent_config:AgentConfig, model:str):
        self.agent_config = agent_config
        openai.api_key = agent_config.OPENAI_API_KEY

    def get_embedding(self, input):
        response = openai.embeddings.create(input=input, model=self.agent_config.EMBEDDING_MODEL)
        return response
