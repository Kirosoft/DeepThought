from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase
from core.llm.llm_base import LLMBase
from datetime import datetime

class AgentLLM:
    def __init__(self, agent_config:AgentConfig):
        self.__agent_config = agent_config
        self.__init_store()

    def __init_store(self):
        # connect to elastic and intialise a connection to the vector store
        self.__db = AgentDBBase(self.__agent_config, self.__agent_config.INDEX_HISTORY)

    def run_inference(self, completed_prompt:str, question:str, role:str, tools: list, routing: list, model) -> object:
        result = {}
        
        # send to the AI bot
        answer_str = ''

        llm = get_llm().bind_functions(tools)
        llm_result = llm.invoke([completed_prompt])

        result["function_call"] = llm_result.additional_kwargs
        result["response"] = llm_result.response_metadata
        result["answer"] = llm_result.content
        result["session_token"] = self.__agent_config.session_token

        # if we are in a session then determine if it is finished or not
        # TODO: not sure if this is needed. Maybe function calling replaces?
        if answer_str.__contains__("**START**"):
            result["session_state"] = False
        else:
            result["session_state"] = True

        # write the answer_str into elastic for the session history
        self.__db.__index(
            document={
                "id": self.__agent_config.session_token, 
                "question": question,
                "answer": llm_result.content,
                "timestamp": datetime.now(),
                "role":role,
                "tools": [tool["name"] for tool in tools],
                "response": llm_result.response_metadata,
                "function_call": llm_result.additional_kwargs,
                "routing": routing
            }
        )
                        
        return result
