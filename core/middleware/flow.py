from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase
from urllib.parse import unquote
import json
import logging
import urllib3

urllib3.disable_warnings()

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

class Flow:

    def __init__(self, agent_config, user_id, tenant):
        self.agent_config = agent_config
        self.db_flows_user = AgentDBBase(self.agent_config, self.agent_config.INDEX_FLOWS, user_id, tenant)

    def load_all_flows(self):
        user_flows = list(self.db_flows_user.get_all())

        return user_flows

    def save_flow(self, flows, level = "user"):
        # TODO: split out flows data to be context seachable?
        flows["level"] = "user"
        return self.db_flows_user.index(flows["name"], flows)


    def get_flow(self, flows_name: str) -> str:
        
        # determine flows, default user_id, default tenant
        result = self.db_flows_user.get(flows_name)
        
        if result is None:
            logging.error(f"Request flows not found {flows_name}")
            return None

        return result
        
    def delete_flow(self, flow_name, level = "user"):
        
        return self.db_flows_user.delete(flow_name)







