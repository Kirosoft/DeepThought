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

    def inference(self, message:str, tools:list[object], llm_type:str = "", llm_model:str = "", temperature = 0.0):

        llm_type = self.agent_config.LLM_TYPE if llm_type == "" else llm_type
        default_model = self.agent_config.OPENAI_MODEL if llm_type == llm_types.OPENAI else self.agent_config.OLLAMA_MODEL
        llm_model = default_model if llm_model == "" else llm_model

        match llm_type:
            case llm_types.OPENAI:
                client =  OpenAI(api_key=self.agent_config.OPENAI_API_KEY)
                completion = client.chat.completions(streaming=False, temperature=temperature, model=llm_model)
                return completion
            
            case llm_types.LLAMA3:
                client = Client(host=self.agent_config.OLLAMA_ENDPOINT)
                options =   {
                    "seed": 101,
                    "temperature": temperature
                    }
                completion = client.chat(model=llm_model, messages=[{'role': 'user','content': message,"options":options}])
                return completion
