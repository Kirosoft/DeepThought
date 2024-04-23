from urllib.parse import unquote
import logging
from datetime import datetime

from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase
from core.agent.agent_memory import AgentMemory
import json

class AgentRole:

    def __init__(self, agent_config : AgentConfig):
        self.__agent_config = agent_config
        self.agent_memory = AgentMemory(agent_config)
        self.__init_store()

    def __init_store(self):
        # connect to elastic and intialise a connection to the vector store
        self.db_roles = AgentDBBase(self.__agent_config, self.__agent_config.INDEX_ROLES)
        self.db_tools = AgentDBBase(self.__agent_config, self.__agent_config.INDEX_TOOLS)
        self.db_specifications = AgentDBBase(self.__agent_config, self.__agent_config.INDEX_SPECIFICATIONS)
        self.db_session = AgentDBBase(self.__agent_config, self.__agent_config.INDEX_HISTORY)

    def __get_role(self, role: str) -> str:
        
        if not hasattr(self, 'role'):
            # determine role
            result = self.db_roles.get(id = role)

            if result is None:
                result = self.db_roles.get(index=self.__agent_config.INDEX_ROLES, id = "default_role")

            self.role = json.loads(unquote(result["prompt"]))

        return self.role

    # rag mode:
    #
    # {% for doc in docs -%}
    # ---
    # NAME: {{ doc.filename }}
    # PASSAGE:
    # {{ doc.page_content }}
    # ---

    # {% endfor -%}

    def is_rag(self, role) -> bool:
        is_rag = False

        try:
            is_rag = role["options"]["rag_mode"]
        except Exception as err:
            logging.info(f"Rag option not set {err}")

        return is_rag
        
    def __is_valid_role(self, role) -> bool:
        return True

    def parse_spec(self, spec) -> object:

        cleaned_spec = unquote(spec["specification"])

        try:
            json_spec = json.loads(cleaned_spec)
        except Exception as err:
            print(f"Unable to parse specification {spec} spec {err}")

        return json_spec
    
    def parse_tool(self, tool) -> object:

        cleaned_tool = unquote(tool["tool"])

        try:
            json_tool = json.loads(cleaned_tool)
        except Exception as err:
            print(f"Unable to parse tool {tool} error {err}")
            json_tool = None

        return json_tool

    def __get_specifications(self, role) -> list[object]:
        specifications = []

        try:
            specification_names = role["specifications"]

            specs = self.db_specifications.multi_get(specification_names)

            specifications = [self.parse_spec(spec) for spec in specs]

        except Exception as err:
            print(f"Unable to find specifications {err}")
        return specifications
    
    def __get_tools(self, role) -> list[object]:
        tool_defs = []

        try:
            tool_names = role["tools"]

            tools = self.db_tools.multi_get(tool_names)

            tool_defs = [self.parse_tool(tool) for tool in tools]

        except Exception as err:
            print(f"Unable to find tool {tools} definition {err}")
        
        return tool_defs

    # loads the role prompt from the database
    # populates the template with context data based on the the supplied user input 'question'
    # the context data search is driven by the template format expecting context data
    # for example the template includes the '{% for doc in docs -%}' expecting data
    # should be inserted
    def get_completed_prompt(self, role_name:str) -> object:
        role = self.__get_role(role_name)
        messages = []
        options = {}

        if (self.__is_valid_role(role)):

            # construct the system prompt
            system_prompt = f"""
                {role["description"]}
                {role["role"]}
                {role["output"]}
            """            

            # build the function message
            # transform the search results into json payload
            if self.is_rag(role):
                for doc in self.agent_memory.get_context(self.__agent_config.input):
                    system_prompt += f"NAME: {doc['path']}"
                    system_prompt += f"CONTENT: {doc['content']}"

            messages.append({"role":"system", "content":system_prompt})

            # session history
            if (not self.__agent_config.new_session):
                session_results = self.agent_memory.get_session_history(self.__agent_config.session_token)
                for session in session_results:
                    messages.append({"role":"user", "content":session["input"]})
                    messages.append({"role":"system", "content":session["answer"]})

            # consuct the latest input as the last message
            user_prompt = {
                "role":"user",
                "content": self.__agent_config.input
            }
            messages.append(user_prompt)

            specifications = self.__get_specifications(role)
            tools  = self.__get_tools(role)

            if "options" in role and "model_override" in role["options"]:
                options["model_override"] = role["options"]["model_override"]

        return {"messages":messages, "tools":tools, "specifications":specifications, "options":options}


 
