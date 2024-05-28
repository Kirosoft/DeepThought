from core.db.agent_db_base import AgentDBBase
from urllib.parse import unquote
import json
import logging
import urllib3
import types

# langchain loaders
from langchain.document_loaders import GithubFileLoader


urllib3.disable_warnings()

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.ERROR)

loader_types = types.SimpleNamespace()
loader_types.GITHUB_FILE_LOADER = "github_file_loader"

class Loader:
    
    __loaders = None
    
    def __init__(self, agent_config, user_id, tenant):
        self.agent_config = agent_config

        if Loader.__loaders is None:
            self.init_loaders()

    def init_loaders(self):
        Loader.__loaders = {}
        self.register_loader(loader_types.GITHUB_FILE_LOADER, [{"name":"repo", "mandatory":True}, {"name":"filter","Mandatory":False}])
                                                                    
    def register_loader(loader_name, loader_args):
        Loader.__loaders[loader_name] = loader_args

    def get_schema(self, loader_name):
        return Loader.__loaders[loader_name] if loader_name in Loader.__loaders else None
         

    def run(self, loaderName, args):

        match loaderName:
            case loader_types.GITHUB_FILE_LOADER:
                    
                    # TODO: validate the supplied args against the registered ones
                    repo = args[0]
                    filter = args[1]

                    loader = GithubFileLoader(
                        repo=repo,
                        # TODO: this key should come from the user profile?
                        access_token=self.agent_config.GITHUB_KEY,
                        github_api_url="https://api.github.com",
                        file_filter=lambda file_path: file_path.endswith(
                            filter
                        ),  
                    )
                    return loader

    def getLoaders(self):
         return Loader.__loaders



