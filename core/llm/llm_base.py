import os
import types
from core.agent.agent_config import AgentConfig
from openai import OpenAI
from ollama import Client

llm_types = types.SimpleNamespace()
llm_types.OPENAI = "openai"
llm_types.LLAMA3 = "llama3"

class LLMBase:
    def __init__(self, agent_config:AgentConfig):
        self.agent_config = agent_config

    def inference(self, llm_type:str, model:str, message:str, tools:list[object], temperature = 0.1):
        match llm_type:
            case llm_types.OPENAI:
                client =  OpenAI(api_key=self.agent_config.OPENAI_API_KEY)
                completion = client.chat.completions(streaming=False, temperature=temperature, model=model)
            case llm_types.LLAMA3:
                client = Client(host=self.agent_config.OLLAMA_ENDPOINT)
                completion = client.chat.completions(model='llama3', messages=[{'role': 'user','content': message}], temperature=temperature)
