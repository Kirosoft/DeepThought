import os
import types
from core.agent.agent_config import AgentConfig
from openai import OpenAI
from ollama import Client
from groq import Groq
from datetime import datetime
import random, string
import json

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
            
    def inference(self, completed_prompt:object, llm_type:str = "", llm_model:str = "", temperature = 0.0):

        if "options" in completed_prompt and "model_override" in completed_prompt["options"]:
            option_parts=completed_prompt["options"]["model_override"].split(":")
            llm_type = option_parts[0]
            llm_model = option_parts[1]

        llm_type = self.agent_config.LLM_TYPE if llm_type == "" else llm_type
        llm_model = self.get_model(llm_type) if llm_model == "" else llm_model

        match llm_type:
            case llm_types.OPENAI:
                client =  OpenAI(api_key=self.agent_config.OPENAI_API_KEY)
                completion = client.chat.completions(streaming=False, temperature=temperature, model=llm_model)

                doc={
                    "id": ''.join(random.choices(string.ascii_letters + string.digits, k=self.agent_config.SESSION_ID_CHARS)), 
                    "input": self.agent_config.input,
                    "finish_reason": completion.choices[0].finish_reason,
                    "tool_calls":  [] if completion.choices[0].finish_reason != "tool_calls" else str(completion.choices[0].message.tool_calls),
                    "answer": completion['message']['content'],
                    "timestamp": datetime.now().isoformat(),
                    "role":self.agent_config.role,
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
                completion = client.chat(model=llm_model, messages=completed_prompt["messages"], tools=completed_prompt["tools"], options=options)

                doc={
                    "id": ''.join(random.choices(string.ascii_letters + string.digits, k=self.agent_config.SESSION_ID_CHARS)), 
                    "input": self.agent_config.input,
                    "finish_reason": completion.choices[0].finish_reason,
                    "tool_calls":  [] if completion.choices[0].finish_reason != "tool_calls" else str(completion.choices[0].message.tool_calls),
                    "answer": completion['message']['content'],
                    "timestamp": datetime.now().isoformat(),
                    "role":self.agent_config.role,
                    "parent_role":self.agent_config.parent_role,
                    "session_token":self.agent_config.session_token
                }
                return doc

            case llm_types.GROQ:
                client = Groq(api_key=self.agent_config.GROK_API_KEY)
                completion = client.chat.completions.create(model=llm_model, messages=completed_prompt["messages"], tools=completed_prompt["tools"], response_format= {"type": "json_object"})
                
                # todo: assumes the answer object schema
                answer_obj = json.loads(completion.choices[0].message.content)
                if not "answer_type" in answer_obj:
                    # TODO: hack because the property moved
                    answer_obj = answer_obj["answer"]
                doc={
                    "id": ''.join(random.choices(string.ascii_letters + string.digits, k=self.agent_config.SESSION_ID_CHARS)), 
                    "input": self.agent_config.input,
                    "finish_reason": completion.choices[0].finish_reason,
                    "tool_calls":  [] if completion.choices[0].finish_reason != "tool_calls" else str(completion.choices[0].message.tool_calls),
                    "answer_type": "" if completion.choices[0].finish_reason == "tool_calls" else answer_obj["answer_type"],
                    "answer": "" if completion.choices[0].finish_reason == "tool_calls" else answer_obj["answer"],
                    "timestamp": datetime.now().isoformat(),
                    "role":self.agent_config.role,
                    "parent_role":self.agent_config.parent_role,
                    "session_token":self.agent_config.session_token
                }
                
                return doc
