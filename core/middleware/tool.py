from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase
from urllib.parse import unquote
import json
import logging

class Tool:

    def __init__(self, agent_config, user_id, tenant):
        self.agent_config = agent_config

        self.db_tools_user = AgentDBBase(self.agent_config, self.agent_config.INDEX_TOOLS, user_id, tenant)
        self.db_tools_system = AgentDBBase(self.agent_config, self.agent_config.INDEX_TOOLS, "system", "system")

    def load_all_tools(self):
        system_tools = [json.loads(unquote(result["prompt"])) for result in self.db_tools_system.get_all()]
        user_tools = [json.loads(unquote(result["prompt"])) for result in self.db_tools_user.get_all()]

        # TODO: tenant tools?
        return { "system_tools": system_tools, "user_tools": user_tools}

    def save_tool(self, tool):
        # TODO: split out tool data to be context seachable?
        self.db_tools.index(tool["name"], tool)

    def get_tool(self, tool_name: str) -> str:
        
        if not hasattr(self, 'tool'):
            # determine tool, default user_id, default tenant
            result = self.db_tools_user.get(tool_name)

            if result is None:
                result = self.db_tools_system.get(tool_name)
                
                if result is None:
                    logging.error(f"Request tool not found {tool_name}")

        return self.tool
    
    def get_tools(self, tool_names) -> list[object]:
        tool_defs = []

        try:
            tools_system = self.db_tools_system.multi_get(tool_names)

            tool_defs += [self.parse_tool(tool) for tool in tools_system]

            # tools_user = self.db_tools_USER.multi_get(tool_names)

            # tool_defs += [self.parse_tool(tool) for tool in tools_user]

        except Exception as err:
            print(f"Unable to find tool {tool_names} definition {err}")
        
        return tool_defs

    def parse_tool(self, tool) -> object:

        cleaned_tool = unquote(tool["tool"])

        try:
            json_tool = json.loads(cleaned_tool)
        except Exception as err:
            print(f"Unable to parse tool {tool} error {err}")
            json_tool = None

        return json_tool




