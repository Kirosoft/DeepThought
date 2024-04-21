import os
import types
from core.agent.agent_config import AgentConfig
from openai import OpenAI
from ollama import Client
from groq import Groq
from datetime import datetime

llm_types = types.SimpleNamespace()
llm_types.OPENAI = "openai"
llm_types.OLLAMA = "ollama"
llm_types.GROQ = "groq"

class LLMBase:
    def __init__(self, agent_config:AgentConfig):
        self.agent_config = agent_config


    def get_model(self, llm_type):

        match llm_type:
            case llm_types.OPENAI:
                return self.agent_config.OPENAI_MODEL
            case llm_types.OLLAMA:
                return self.agent_config.OLLAMA_MODEL
            case llm_types.GROQ:
                return self.agent_config.GROK_MODEL
            
    def inference(self, message:str, tools:list[object], llm_type:str = "", llm_model:str = "", temperature = 0.0):

        llm_type = self.agent_config.LLM_TYPE if llm_type == "" else llm_type
        llm_model = self.get_model(llm_type) if llm_model == "" else llm_model

        match llm_type:
            case llm_types.OPENAI:
                client =  OpenAI(api_key=self.agent_config.OPENAI_API_KEY)
                completion = client.chat.completions(streaming=False, temperature=temperature, model=llm_model)

                # TODO: fix this
                doc={
                    "id": self.agent_config.session_token, 
                    "input": self.agent_config.input,
                    "answer": completion.choices[0].message.content,
                    "timestamp": datetime.now().isoformat(),
                    "role":self.agent_config.role,
    #                "tools": [tool["name"] for tool in self.tools],
                    "response": completion.response_metadata,
                    "function_call": completion.additional_kwargs,
    #                "routing": self.routing,
                    "parent_role":self.agent_config.parent_role,
                    "session_token":self.agent_config.session_token
                }

                return completion
            
            case llm_types.OLLAMA:
                client = Client(host=self.agent_config.OLLAMA_ENDPOINT)
                options =   {
                    "seed": 101,
                    "temperature": temperature
                    }
                completion = client.chat(model=llm_model, messages=[{'role': 'assistant','content': message,"options":options}])

                doc={
                    "id": self.agent_config.session_token, 
                    "input": self.agent_config.input,
                    "answer": completion['message']['content'],
                    "timestamp": datetime.now().isoformat(),
                    "role":self.agent_config.role,
    #                "tools": [tool["name"] for tool in self.tools],
    #                "response": llm_result.response_metadata,
    #                "function_call": llm_result.additional_kwargs,
    #                "routing": self.routing,
                    "parent_role":self.agent_config.parent_role,
                    "session_token":self.agent_config.session_tokenxreal
                }
                return doc

            case llm_types.GROQ:
                client = Groq(api_key=self.agent_config.GROK_API_KEY)
                completion = client.chat.completions.create(model=llm_model, messages=[{'role': 'system','content': message}])

                doc={
                    "id": self.agent_config.session_token, 
                    "input": self.agent_config.input,
                    "answer": completion.choices[0].message.content,
                    "timestamp": datetime.now().isoformat(),
                    "role":self.agent_config.role,
    #                "tools": [tool["name"] for tool in self.tools],
    #                "response": llm_result.response_metadata,
    #                "function_call": llm_result.additional_kwargs,
    #                "routing": self.routing,
                    "parent_role":self.agent_config.parent_role,
                    "session_token":self.agent_config.session_token
                }
                
                return doc
