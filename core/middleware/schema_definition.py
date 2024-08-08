from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase
from urllib.parse import unquote
import json
import logging

class SchemaDefinition:

    def __init__(self, agent_config:AgentConfig, user_id, tenant):
        self.agent_config = agent_config
        self.db_schema_definition_user = AgentDBBase(self.agent_config, self.agent_config.INDEX_SPECS, user_id, tenant)
        self.db_schema_definition_system = AgentDBBase(self.agent_config, self.agent_config.INDEX_SPECS, "system", "system")

    def load_all_schema_definitions(self):
        system_schema_definition = [json.loads(unquote(result["prompt"])) for result in self.db_schema_definition_system.get_all()]
        user_schema_definition = [json.loads(unquote(result["prompt"])) for result in self.db_schema_definition_user.get_all()]

        # TODO: tenant spec?
        return { "system_schema_definition": system_schema_definition, "user_schema_definition": user_schema_definition}

    def get_schema_definitions(self, schema_definition_names) -> list[str]:
        schema_definitions = []

        try:
            schema_definitions += ([definition['specification'].strip() for definition in list(self.db_schema_definition_user.multi_get(schema_definition_names))])
            schema_definitions += ([definition['specification'].strip() for definition in list(self.db_schema_definition_system.multi_get(schema_definition_names))])

        except Exception as err:
            print(f"Unable to find schema_definitions {err}")
        return schema_definitions
    
    def save_schema_definition(self, schema_definition):
        # TODO: split out spec data to be context seachable?
        self.db_schema_definition_user.index(schema_definition["name"], schema_definition)

    def get_schema_definition(self, schema_definition_name: str) -> str:
        
        # determine schema specification, default user_id, default tenant
        result = self.db_schema_definition_user.get(schema_definition_name)

        if result is None:
            result = self.db_schema_definition_system.get(schema_definition_name)
            
            if result is None:
                logging.error(f"Requested schema definition not found {schema_definition_name}")

        return result
    
    def parse_schema_definition(self, schema_definition) -> object:

        cleaned_schema_definition = unquote(schema_definition["spec"])

        try:
            json_schema_definition = json.loads(cleaned_schema_definition)
        except Exception as err:
            print(f"Unable to parse schema definition {schema_definition} - {err}")

        return json_schema_definition

    

        







