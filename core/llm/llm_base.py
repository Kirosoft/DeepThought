import os
import types
from core.agent.agent_config import AgentConfig
from openai import OpenAI
from ollama import Client
from groq import Groq
from datetime import datetime
import random, string
import json
import anthropic
import logging

llm_types = types.SimpleNamespace()
llm_types.OPENAI = "openai"
llm_types.OLLAMA = "ollama"
llm_types.GROQ = "groq"
llm_types.ANTHROPIC = "anthropic"

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
            case llm_types.ANTHROPIC:
                return self.agent_config.ANTHROPIC_MODEL
            
    def process_ai_completion(self, completion, role):
        # todo: assumes the answer object schema
        answer = completion.choices[0].message.content
        answer_type = ""
        tool_name = ''
        tool_arguments = ''
        tool_result = ''

        # TODO: support multiple tool calls
        if completion.choices[0].finish_reason =="tool_calls":
            tool_call = completion.choices[0].message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_arguments = json.dumps(tool_call.function.arguments)
            answer_type ="tool_calls"
            tool_result = {
                "role":"assistant",
                "content": None,
                "tool_calls": [{
                                    "id":tool_call.id,
                                    "function":{
                                        "name": tool_name,
                                        "arguments":tool_arguments, 
                                    },
                                    "type": "function"
                }]
            }
        elif answer.__contains__("**FINISHED**"):
            answer_type="complete"
        else:
            answer_type="user_input_needed"

        doc={
            "id": ''.join(random.choices(string.ascii_letters + string.digits, k=self.agent_config.SESSION_ID_CHARS)), 
            "input": self.agent_config.input,
            "finish_reason": completion.choices[0].finish_reason,
            "tool_calls":  [] if completion.choices[0].finish_reason != "tool_calls" else str(completion.choices[0].message.tool_calls),
            "tool_name": tool_name,
            "tool_arguments": tool_arguments,
            "answer_type": answer_type,     # TODO: deprecate
            "answer": tool_result if completion.choices[0].finish_reason == "tool_calls" else answer,
            "timestamp": datetime.now().isoformat(),
            "role":role,
            "parent_role":self.agent_config.parent_role,
            "session_token":self.agent_config.session_token
        }

        return doc

    def process_ai_error(self, error, role):
        # todo: assumes the answer object schema
        answer = str(error)
        answer_type = ""


        doc={
            "id": ''.join(random.choices(string.ascii_letters + string.digits, k=self.agent_config.SESSION_ID_CHARS)), 
            "input": self.agent_config.input,
            "finish_reason": answer,
            "tool_calls":  [] ,
            "answer_type": answer_type,
            "answer": answer,
            "timestamp": datetime.now().isoformat(),
            "role":role,
            "parent_role":self.agent_config.parent_role,
            "session_token":self.agent_config.session_token
        }

        return doc
    
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
                #completion = client.chat.completions.create(model=llm_model, messages=completed_prompt["messages"], tools=completed_prompt["tools"])
                
                try:
                    completion = client.chat.completions.create(model=llm_model, messages=completed_prompt["messages"], 
                                                            tools = None if len(completed_prompt['tools']) == 0 else completed_prompt['tools'], response_format=completed_prompt['schema'])

                except Exception as e:
                    logging.error(f'inference error {str(e)}')
                    return self.process_ai_error(e, completed_prompt["role"])
                
                return self.process_ai_completion(completion, completed_prompt["role"])

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
                    "role": completed_prompt["role"],
                    "parent_role":self.agent_config.parent_role,
                    "session_token":self.agent_config.session_token
                }
                return doc

            case llm_types.GROQ:
                client = Groq(api_key=self.agent_config.GROK_API_KEY)
                completion = client.chat.completions.create(model=llm_model, messages=completed_prompt["messages"], tools=completed_prompt["tools"])
                
                doc = self.process_ai_completion(completion)
                
                return doc

            case llm_types.ANTHROPIC:
                client = anthropic.Anthropic(api_key=self.agent_config.ANTHROPIC_API_KEY)
                completion = client.messages.create(model=llm_model, messages=completed_prompt["messages"], tools=completed_prompt["tools"])
                
                doc = self.process_ai_completion(completion)
                
                return doc
