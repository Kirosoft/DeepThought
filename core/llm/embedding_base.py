import os
import types
from core.agent.agent_config import AgentConfig
from openai import OpenAI

embedding_types = types.SimpleNamespace()
embedding_types.OPENAI = "openai"
embedding_types.LLAMA3 = "llama3"

class EmbeddingeddingBase:
    def __init__(self, agent_config:AgentConfig, model:str):
        self.model = self.__init_embedding(model)
        self.agent_config = agent_config

    def __init_embedding(self, embedding_type:str, model:str, temperature):
        match embedding_type:
            case embedding_types.OPENAI:
                client =  OpenAI(api_key=self.agent_config.OPENAI_API_KEY)
                completion = client.chat.completions(streaming=False, temperature=temperature, model=model)
                return completion

