from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase
from urllib.parse import unquote
import json
import logging

class Spec:

    def __init__(self, agent_config:AgentConfig, user_id, tenant):
        self.agent_config = agent_config
        self.db_spec_user = AgentDBBase(self.agent_config, self.agent_config.INDEX_SPECS, user_id, tenant)
        self.db_spec_system = AgentDBBase(self.agent_config, self.agent_config.INDEX_SPECS, "system", "system")

    def load_all_specs(self):
        system_spec = [json.loads(unquote(result["prompt"])) for result in self.db_spec_system.get_all()]
        user_spec = [json.loads(unquote(result["prompt"])) for result in self.db_spec_user.get_all()]

        # TODO: tenant spec?
        return { "system_spec": system_spec, "user_spec": user_spec}

    def get_specs(self, spec_names) -> list[str]:
        specs = []

        try:
            specs += ([spec['specification'].strip() for spec in list(self.db_spec_user.multi_get(spec_names))])
            specs += ([spec['specification'].strip() for spec in list(self.db_spec_system.multi_get(spec_names))])

        except Exception as err:
            print(f"Unable to find specs {err}")
        return specs
    
    def save_spec(self, spec):
        # TODO: split out spec data to be context seachable?
        self.db_spec.index(spec["name"], spec)

    def get_spec(self, spec_name: str) -> str:
        
        if not hasattr(self, 'spec'):
            # determine spec, default user_id, default tenant
            result = self.db_spec_user.get(spec_name)

            if result is None:
                result = self.db_spec_system.get(spec_name)
                
                if result is None:
                    logging.error(f"Request spec not found {spec_name}")

        return self.spec
    
    def parse_spec(self, spec) -> object:

        cleaned_spec = unquote(spec["spec"])

        try:
            json_spec = json.loads(cleaned_spec)
        except Exception as err:
            print(f"Unable to parse spec {spec} spec {err}")

        return json_spec

    

        







