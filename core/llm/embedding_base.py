import os
import types
from core.agent_config import AgentConfig
from openai import OpenAI

llm_types = types.SimpleNamespace()
llm_types.OPENAI = "openai"
llm_types.LLAMA3 = "llama3"

class LLMBase:
    def __init__(self, agent_config:AgentConfig, model:str):
        self.model = self.__init_llm(model)
        self.agent_cofnig = agent_config

    def __init_llm(self, model:str, temperature):
        match model:
            case llm_types.OPENAI:
                client =  OpenAI(api_key=self.agent_config.OPENAI_API_KEY)
                
                completion = client.chat.completions(streaming=False, temperature=temperature, model=model)
