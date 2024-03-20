from core.agent_config import AgentConfig
from utils.llm_integrations import get_llm
from elasticsearch import Elasticsearch
from datetime import datetime
class AgentLLM:
    def __init__(self, agent_config:AgentConfig):
        self.__agent_config = agent_config
        self.__init_store()

    def __init_store(self):
        # connect to elastic and intialise a connection to the vector store
        self.__db = Elasticsearch(cloud_id=self.__agent_config.ELASTIC_CLOUD_ID, api_key=self.__agent_config.ELASTIC_API_KEY)

    def run_inference(self, completed_prompt:str, question:str, role:str, tools: list) -> object:
        result = {}
        
        # send to the AI bot
        answer_str = ''
        llm = get_llm()
        for chunk in llm.stream(completed_prompt):
            answer_str += chunk.content

        result["answer"] = answer_str
        result["session_token"] = self.__agent_config.session_token

        # if we are in a session then determine if it is finished or not
        if (self.__agent_config.session_state):
            if answer_str.__contains__("FINISHED"):
                result["session_state"] = False
            else:
                result["session_state"] = True

        # write the answer_str into elastic for the session history
        self.__db.index(
            index=self.__agent_config.ES_INDEX_HISTORY,
            document={
                "session_token": self.__agent_config.session_token,
                "question": question,
                "answer": answer_str,
                "timestamp": datetime.now(),
                "role":role
            }
        )
                        
        return result
