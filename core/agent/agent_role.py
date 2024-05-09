from urllib.parse import unquote
import logging
from datetime import datetime

from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase
from core.agent.agent_memory import AgentMemory
import json

class AgentRole:

    def __init__(self, agent_config : AgentConfig, tenant, user_id):
        self.__agent_config = agent_config
        self.agent_memory = AgentMemory(agent_config, tenant, user_id)
        self.__init_store()

    def __init_store(self):
        # connect to elastic and intialise a connection to the vector store
        # TODO: make sure the tenant and userid are used to form a hierarchical key
        self.db_roles = AgentDBBase(self.__agent_config, self.__agent_config.INDEX_ROLES, "/roles")
        self.db_tools = AgentDBBase(self.__agent_config, self.__agent_config.INDEX_TOOLS, "/tools")
        self.db_specs = AgentDBBase(self.__agent_config, self.__agent_config.INDEX_SPECS, "/specs")
        self.db_session = AgentDBBase(self.__agent_config, self.__agent_config.INDEX_HISTORY, "/history")

    def __get_role(self, role: str) -> str:
        
        if not hasattr(self, 'role'):
            # determine role
            result = self.db_roles.get(id = role)

            if result is None:
                result = self.db_roles.get(id = "default_role")

            self.role = json.loads(unquote(result["prompt"]))

        return self.role

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

        cleaned_spec = unquote(spec["spec"])

        try:
            json_spec = json.loads(cleaned_spec)
        except Exception as err:
            print(f"Unable to parse spec {spec} spec {err}")

        return json_spec
    
    def parse_tool(self, tool) -> object:

        cleaned_tool = unquote(tool["tool"])

        try:
            json_tool = json.loads(cleaned_tool)
        except Exception as err:
            print(f"Unable to parse tool {tool} error {err}")
            json_tool = None

        return json_tool

    def __get_specs(self, spec_names) -> list[str]:
        specs = []

        try:
            specs = [spec['specification'].strip() for spec in list(self.db_specs.multi_get(spec_names))]

        except Exception as err:
            print(f"Unable to find specs {err}")
        return specs
    
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
            
            # user can override the examples 
            output_format_json = self.__get_specs(role['output_format']) if 'output_format' in role else []

            # construct the system prompt
            # TODO: detect if the output is a spec and prompt the whole spec as JSON {spec}
            system_prompt = f"""
                {role["description"]}
                {role["role"]}
                {f"Expected input: {role['expected_input']}" if role['expected_input'] != "" else ""}
                {f"Think about your response. If all the INPUT was provided and the OUTPUT seems complete, OUTPUT [[**FINISHED**]] OR [[**NOT_FINISHED**]] if not finished. You *MUST* output one or the other based on the circumstances."}
                {f"Example output: {role['examples']}" if role['examples'] != "" else ""}
                {f"output format: JSON SCHEMA [{','.join(output_format_json)}] do not invent any new fields or change the output scehma in any way. Any UNESCAPED characters should be escaped. Ensuer there are no NEWLINE characters inserted. Ensure there are no back slashes or enescaped characters.The answer to the user should just be text and not JSON" if len(output_format_json) != 0 else ""}
            """           

            # build the function message
            # transform the search results into json payload
            if self.is_rag(role):
                for doc in self.agent_memory.get_context(self.__agent_config.input):
                    system_prompt += f"NAME: {doc['path']}"
                    system_prompt += f"CONTENT: {doc['content']}"

            messages.append({"role":"system", "content":system_prompt})

            # session history
            # TODO: does the session history need to be sequenced to replay in the right order?
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

            tools  = self.__get_tools(role)

            if "options" in role and "model_override" in role["options"]:
                options["model_override"] = role["options"]["model_override"]

        return {"messages":messages, "tools":tools, "options":options, "output_format_json":output_format_json}


 
