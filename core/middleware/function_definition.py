from core.db.agent_db_base import AgentDBBase
from urllib.parse import unquote
import json
import logging
from core.middleware.context import Context
from  core.utils.schema import create_dynamic_model

class FunctionDefinition:

    def __init__(self, agent_config, user_id, tenant):
        self.agent_config = agent_config

        self.db_functions_user = AgentDBBase(self.agent_config, self.agent_config.INDEX_FUNCTIONS, user_id, tenant)
        self.db_functions_system = AgentDBBase(self.agent_config, self.agent_config.INDEX_FUNCTIONS, "system", "system")
        self.user_id = user_id
        self.tenant = tenant
        self.context_manager = Context(agent_config, user_id, tenant)

    def load_all_function_definitions(self):
        system_functions = [json.loads(unquote(result["prompt"])) for result in self.db_functions_system.get_all()]
        user_functions = [json.loads(unquote(result["prompt"])) for result in self.db_functions_user.get_all()]

        # TODO: tenant functions?
        return { "system_functions": system_functions, "user_functions": user_functions}

    def save_function_definition(self, function):
        # TODO: split out function data to be context seachable?
        self.db_functions_user.index(function["name"], function)

    def get_function_definition(self, function_name: str) -> str:
        
        # determine function, default user_id, default tenant
        result = self.db_functions_user.get(function_name)

        if result is None:
            result = self.db_functions_system.get(function_name)
            
            if result is None:
                logging.error(f"Request function not found {function_name}")

        if result is not None and "options" in result and "schema_override_context" in result["options"]:
            try:
                context_data_db = self.context_manager.get_latest_context_data(result["options"]["schema_override_context"])
                function_override_context = AgentDBBase(self.agent_config, context_data_db, self.user_id, self.tenant)
                override_function_definition = function_override_context.get(result["name"]+".function")

                # convert to a formal json schema
                schema_obj = json.loads(override_function_definition["content"])
                schema_model = create_dynamic_model(schema_obj).schema()
                #schema_model["name"]=role["name"]
                schema = {"type":"function", "function":{"name":function_name, "description": schema_obj["description"] if "description" in schema_obj else function_name, "parameters": schema_model}, "strict":True}

                result["schema"] = schema
            except Exception as err:
                logging.error(f"Failed to define schema for {err}")
        return result
    
    def get_function_definitions(self, function_names) -> list[object]:
        function_defs = []

        try:
            function_defs = [self.get_function_definition(func_name) for func_name in function_names]

        except Exception as err:
            print(f"Unable to find function {function_names} definition {err}")
        
        return function_defs

    def get_function_schemas(self, function_names) -> list[object]:
        function_defs = []

        try:
            function_defs = [self.get_function_definition(func_name)["schema"] for func_name in function_names]

        except Exception as err:
            print(f"Unable to find function {function_names} definition {err}")
        
        return function_defs

    def parse_function_definition(self, function_definition) -> object:

        cleaned_function = unquote(function_definition["function"])

        try:
            json_function = json.loads(cleaned_function)
        except Exception as err:
            print(f"Unable to parse function definition {function_definition} error {err}")
            json_function = None

        return json_function
    



