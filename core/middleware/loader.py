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
        self.user_id = user_id
        self.tenant = tenant

        if Loader.__loaders is None:
            self.init_loaders()

        self.userdb = AgentDBBase(agent_config, agent_config.INDEX_USER, user_id, tenant)
        self.user_keys = None

    def init_loaders(self):
        Loader.__loaders = {}
        self.register_loader(loader_types.GITHUB_FILE_LOADER, [
                {"name":"repo", "mandatory":True}, 
                {"name":"filter","mandatory":False, "default":".*"}, 
                {"name":"github_api_url","mandatory": False, "default":"https://api.github.com" },
                {"name":"github_key","mandatory": True, "default":"$GITHUB_API_KEY" }
            ])
                                                                    
    def register_loader(loader_name, loader_args):
        Loader.__loaders[loader_name] = loader_args

    def get_schema(self, loader_name):
        return Loader.__loaders[loader_name] if loader_name in Loader.__loaders else None
    
    def resolve_variables(self, arg):

        # see if the arg needs to resolved to a user setting
        if arg[0] == "$":
            if self.user_keys is None:
                user_settings = self.userdb.get(self.user_id)
                self.user_keys = user_settings["keys"] if "keys" in user_settings else None
                
                if user_settings is None:
                    raise(f"Missing user settings ${self.user_id} ${self.tenant}")

            # resolve the value in user keys if available            
            return self.user_keys[arg[1:]] if arg[1:] in self.user_keys else arg

    def get_args(self, loader_args,input_args):
        result_args = {}

        for arg in loader_args:
            # arg found as supplied in the input
            if arg in input_args:
                result_args[arg] = self.resolve_variables(input_args[arg])
            elif arg["mandatory"] and "default" in arg:
                result_args[arg] = self.resolve_variables(arg["default"])
            elif arg["mandatory"]:
                raise(f'Missing mandatory {arg["name"]}')
            else:
                # missing but not mandatory
                pass

    def run(self, loader_name, input_args):

        match loader_name:
            case loader_types.GITHUB_FILE_LOADER:
                    
                    try: 
                        loader_args_spec = Loader.__loaders(loader_name)
                        loader_args  = self.get_args(loader_args_spec, input_args)

                        loader = GithubFileLoader(
                            repo=loader_args["repo"],
                            # TODO: this key should come from the user profile?
                            access_token=loader_args["github_key"],
                            github_api_url=loader_args["github_api_ul"],
                            file_filter=lambda file_path: file_path.endswith(
                                loader_args["filter"]
                            ),  
                        )
                    except:
                        return None

                    return loader





