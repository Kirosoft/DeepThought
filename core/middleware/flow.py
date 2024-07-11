from core.agent.agent_config import AgentConfig
from core.db.agent_db_base import AgentDBBase
from urllib.parse import unquote
import json
import logging
import urllib3
from collections import deque, defaultdict

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

    def find_nodes(self, graph, node_type):
        return [node for node in graph["nodes"] if node["type"]==node_type]

    def get_node_from_id(self, graph, node_id):
        for node in graph["nodes"]:
            if node["id"]==node_id:
                return node
        
        return None

    def get_linked_nodes(self, graph, current_node):
        node_lookup = {}
        linked_nodes = []
        nodes = graph["nodes"]
        links = graph["links"]
        link_lookup = {}

        for link in links:
            link_lookup[link[0]] = link
        for node in nodes:
            node_lookup[node["id"]]=node

        link_groups = [output for output in node_lookup[current_node["id"]]["outputs"] if output["links"] is not None]

        for link_group in link_groups:
            if link_group["links"] is not None:
                for link_id in link_group["links"]:
                    neighbour_id = link_lookup[link_id][3]
                    linked_nodes.append(node_lookup[neighbour_id])

        return linked_nodes
    

    # returns the execution order for the input graph
    def topological_sort(self, graph, from_node_id = -1):
        # Initialize the in-degree dictionary
        in_degree = defaultdict(int)
        node_lookup = {}
        nodes = graph["nodes"]
        links = graph["links"]
        link_lookup = {}

        for link in links:
            link_lookup[link[0]] = link

        for node in nodes:
            node_lookup[node["id"]]=node
  
        for node in nodes:
            for output in node["outputs"]:
                if output["links"] is not None:
                    for link_id in output["links"]:
                        neighbour_id = link_lookup[link_id][3]
                        in_degree[neighbour_id] += 1
        
        # Queue for nodes with no incoming edges (in-degree of 0)
        queue = deque([node for node in nodes if in_degree[node["id"]] == 0])
        sorted_order = []

        while queue:
            node = queue.popleft()
            sorted_order.append(node)
            # Visit each dependency of the node and reduce its in-degree
            link_groups = [output for output in node_lookup[node["id"]]["outputs"] if output["links"] is not None]
            for link_group in link_groups:
                if link_group["links"] is not None:
                    for link_id in link_group["links"]:
                        neighbour_id = link_lookup[link_id][3]
                        in_degree[neighbour_id] -= 1
                        if in_degree[neighbour_id] == 0:
                            queue.append(node_lookup[neighbour_id])

        # If sorted_order contains all nodes, we have a successful topological sort
        if len(sorted_order) == len(nodes):
            return sorted_order
        else:
            # There was a cycle or some nodes weren't reachable
            raise ValueError("Graph has at least one cycle or unconnected components, which prevents topological sorting.")



